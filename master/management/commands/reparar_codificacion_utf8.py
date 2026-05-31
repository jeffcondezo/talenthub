"""
Repara textos donde caracteres acentuados del español fueron guardados como '??'.

Ocurre cuando la conexión MySQL no usaba utf8mb4 al insertar datos.
"""
import re
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models

ACCENT_CHARS = 'áéíóúñüÁÉÍÓÚÑÜ'

KNOWN_PHRASES = [
    ('Universidad Nacional de Ingenier??a', 'Universidad Nacional de Ingeniería'),
    ('Ingenier??a de Sistemas', 'Ingeniería de Sistemas'),
    ('Universidad del Pac??fico', 'Universidad del Pacífico'),
    ('Lima, Per??', 'Lima, Perú'),
    ('Cusco, Per??', 'Cusco, Perú'),
    ('Mar??a Gonz??lez', 'María González'),
    ('??ncash', 'Áncash'),
    ('Apur??mac', 'Apurímac'),
    ('Hu??nuco', 'Huánuco'),
    ('Anc??n', 'Ancón'),
    ('Bre??a', 'Breña'),
    ('Jes??s', 'Jesús'),
    ('Ca??ete', 'Cañete'),
    ('Huarochir??', 'Huarochirí'),
    ('Oy??n', 'Oyón'),
]


def load_vocabulary(base_dir):
    """Vocabulario de referencia para reconstruir palabras con ??."""
    words = set()

    sql_path = base_dir / 'talenthub.sql'
    if sql_path.exists():
        text = sql_path.read_text(encoding='utf-8', errors='ignore')
        words.update(re.findall(r'[A-Za-zÀ-ÖØ-öø-ÿ]+', text))

    for model in apps.get_app_config('master').get_models():
        for field in model._meta.get_fields():
            if hasattr(field, 'choices') and field.choices:
                for value, label in field.choices:
                    if isinstance(label, str):
                        words.update(re.findall(r'[A-Za-zÀ-ÖØ-öø-ÿ]+', label))

    extra = [
        'Perú', 'Pacífico', 'Ingeniería', 'María', 'González', 'Jesús', 'Breña',
        'Ancón', 'Áncash', 'Apurímac', 'Huánuco', 'Cañete', 'Huarochirí', 'Oyón',
        'tecnologías', 'análisis', 'diseño', 'diseñador', 'máxima', 'código', 'años',
        'Inglés', 'selección', 'capacitación', 'políticas', 'desempeño', 'metodologías',
        'ágiles', 'gestión', 'básico', 'investigación', 'programación', 'sólido',
        'Administración', 'administración', 'función', 'Comunicación', 'operación',
        'especialización', 'evaluación', 'organización', 'producción', 'distribución',
        'solución', 'decisión', 'versión', 'misión', 'visión', 'dimensión', 'expansión',
        'inversión', 'descripción', 'ubicación', 'requisitos', 'experiencia',
    ]
    words.update(extra)

    return {w.lower(): w for w in words if w}


def _match_case(template, original):
    if original.isupper():
        return template.upper()
    if original[0].isupper():
        return template[0].upper() + template[1:]
    return template


KNOWN_WORDS = {
    'Per??': 'Perú',
    'per??': 'perú',
    'PER??': 'PERÚ',
}


def fix_word(word, vocab):
    if '??' not in word:
        return word

    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word]

    if word.count('??') == 1:
        matches = []
        for ch in ACCENT_CHARS:
            candidate = word.replace('??', ch, 1)
            ref = vocab.get(candidate.lower())
            if ref:
                matches.append(_match_case(ref, word))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            for m in matches:
                if m.lower() in ('perú', 'maría', 'inglés', 'pacífico'):
                    return m

    return word


def fix_text(value, vocab):
    if not value or '??' not in value:
        return value

    text = value
    for bad, good in sorted(KNOWN_PHRASES, key=lambda x: -len(x[0])):
        text = text.replace(bad, good)

    if '??' not in text:
        return text

    parts = re.split(r'(\s+)', text)
    fixed = []
    for part in parts:
        if part.strip() and '??' in part:
            fixed.append(fix_word(part, vocab))
        else:
            fixed.append(part)
    return ''.join(fixed)


class Command(BaseCommand):
    help = "Repara textos con '??' en lugar de caracteres acentuados (UTF-8)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra cambios sin guardar en la base de datos.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        vocab = load_vocabulary(Path(__file__).resolve().parents[3])
        updated_rows = 0
        updated_fields = 0

        for model in apps.get_app_config('master').get_models():
            text_fields = [
                f for f in model._meta.get_fields()
                if isinstance(f, (models.CharField, models.TextField))
                and not f.primary_key
            ]
            if not text_fields:
                continue

            for obj in model.objects.all().iterator():
                changes = {}
                for field in text_fields:
                    val = getattr(obj, field.name)
                    if not isinstance(val, str) or '??' not in val:
                        continue
                    new_val = fix_text(val, vocab)
                    if new_val != val:
                        changes[field.name] = new_val

                if not changes:
                    continue

                updated_rows += 1
                updated_fields += len(changes)
                label = str(obj)
                for name, new_val in changes.items():
                    old_val = getattr(obj, name)
                    preview_old = (old_val[:60] + '…') if len(old_val) > 60 else old_val
                    preview_new = (new_val[:60] + '…') if len(new_val) > 60 else new_val
                    self.stdout.write(f'{model.__name__} #{obj.pk} {name}:')
                    self.stdout.write(f'  - {preview_old}')
                    self.stdout.write(f'  + {preview_new}')

                if not dry_run:
                    model.objects.filter(pk=obj.pk).update(**changes)

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'Dry-run: {updated_rows} registros / {updated_fields} campos por corregir.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Corregidos {updated_rows} registros ({updated_fields} campos).'
            ))
