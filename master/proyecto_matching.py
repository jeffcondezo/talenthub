"""Matching de colaboradores por skills registrados en la persona (evaluación RRHH)."""
from django.db.models import Prefetch

from .models import Colaborador, PersonaSkill


def _normalize(text):
    return (text or '').strip().lower()


def _get_or_create_skill(nombre):
    from .models import Skill

    skill = Skill.objects.filter(nombre__iexact=nombre).first()
    if not skill:
        skill = Skill.objects.create(nombre=nombre.strip(), tipo='TECNICA')
    return skill


def sync_persona_skills(persona, nombres, user=None):
    """Reemplaza los skills de la persona por la lista de nombres."""
    nombres = parse_skills_texto(nombres or '')
    keep_ids = []
    for nombre in nombres:
        skill = _get_or_create_skill(nombre)
        ps, created = PersonaSkill.objects.get_or_create(
            persona=persona,
            skill=skill,
            defaults={'registrado_por': user},
        )
        if not created and user and not ps.registrado_por_id:
            ps.registrado_por = user
            ps.save(update_fields=['registrado_por', 'fecha_actualizacion'])
        keep_ids.append(ps.id)
    PersonaSkill.objects.filter(persona=persona).exclude(id__in=keep_ids).delete()
    return list(
        PersonaSkill.objects.filter(persona=persona)
        .select_related('skill')
        .order_by('skill__nombre')
    )


def colaboradores_qs_para_matching():
    return (
        Colaborador.objects.filter(estado_laboral='ACTIVO', persona__isnull=False)
        .select_related('persona', 'cargo')
        .prefetch_related(
            Prefetch(
                'persona__persona_skills',
                queryset=PersonaSkill.objects.select_related('skill'),
            ),
            'asignaciones_proyecto',
        )
    )


def _persona_skill_names(persona):
    if not persona:
        return set()
    names = set()
    for ps in persona.persona_skills.all():
        if ps.skill_id and ps.skill.nombre:
            names.add(_normalize(ps.skill.nombre))
    return names


def score_colaborador_contra_skills(colaborador, skills):
    """
    Compara skills del proyecto vs skills registrados en la persona.
    skills: iterable de Skill o strings.
    """
    skill_names = []
    for s in skills:
        nombre = s.nombre if hasattr(s, 'nombre') else str(s)
        if nombre and nombre.strip():
            skill_names.append(nombre.strip())

    if not skill_names:
        return {
            'score': 0,
            'matched': [],
            'missing': [],
            'horas_otras': 0,
            'match_count': 0,
            'total_skills': 0,
        }

    registrados = _persona_skill_names(colaborador.persona if colaborador.persona_id else None)

    matched = []
    missing = []
    for nombre in skill_names:
        if _normalize(nombre) in registrados:
            matched.append(nombre)
        else:
            # match parcial por contención (ej. "React Native" vs "React")
            key = _normalize(nombre)
            hit = any(key == r or key in r or r in key for r in registrados if len(r) >= 3)
            if hit:
                matched.append(nombre)
            else:
                missing.append(nombre)

    total = len(skill_names)
    score = int(round(100.0 * len(matched) / total)) if total else 0

    horas_otras = sum(
        a.horas_semanales
        for a in colaborador.asignaciones_proyecto.all()
        if a.activo
    )

    return {
        'score': score,
        'matched': matched,
        'missing': missing,
        'horas_otras': horas_otras,
        'match_count': len(matched),
        'total_skills': total,
    }


def rank_colaboradores_por_skills(skills, exclude_ids=None, min_score=0):
    """Lista de dicts ordenados por score desc, luego menor carga horaria."""
    exclude_ids = set(exclude_ids or [])
    resultados = []
    for col in colaboradores_qs_para_matching():
        if col.id in exclude_ids:
            continue
        meta = score_colaborador_contra_skills(col, skills)
        if meta['score'] < min_score and meta['total_skills'] and min_score > 0:
            continue
        resultados.append({
            'colaborador': col,
            'persona': col.persona,
            **meta,
        })
    resultados.sort(
        key=lambda r: (-r['score'], r['horas_otras'], r['persona'].apellido_paterno or '')
    )
    return resultados


def parse_skills_texto(texto):
    """Separa skills por coma o salto de línea."""
    if not texto:
        return []
    if isinstance(texto, (list, tuple)):
        raw_items = []
        for item in texto:
            raw_items.extend(str(item).replace('\n', ',').split(','))
    else:
        raw_items = str(texto).replace('\n', ',').split(',')
    seen = set()
    out = []
    for item in raw_items:
        name = item.strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out
