#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talenthub.settings')
django.setup()

from master.models import (
    Persona, CV, Convocatoria, Postulacion, FormacionAcademica, 
    ExperienciaLaboral, Area, Cargo
)

def crear_datos_prueba():
    print("Creando datos de prueba...")
    
    # Crear áreas
    area_tech, created = Area.objects.get_or_create(
        nombre="Tecnología",
        defaults={
            'descripcion': 'Área de tecnología e informática',
            'activo': True
        }
    )
    
    area_marketing, created = Area.objects.get_or_create(
        nombre="Marketing",
        defaults={
            'descripcion': 'Área de marketing y comunicaciones',
            'activo': True
        }
    )
    
    area_finanzas, created = Area.objects.get_or_create(
        nombre="Finanzas",
        defaults={
            'descripcion': 'Área de finanzas y contabilidad',
            'activo': True
        }
    )
    
    # Crear cargos
    cargo_dev, created = Cargo.objects.get_or_create(
        nombre="Desarrollador Full Stack Senior",
        defaults={
            'area': area_tech,
            'descripcion': 'Desarrollador con experiencia en frontend y backend',
            'nivel': 'Senior',
            'activo': True
        }
    )
    
    cargo_marketing, created = Cargo.objects.get_or_create(
        nombre="Especialista en Marketing Digital",
        defaults={
            'area': area_marketing,
            'descripcion': 'Especialista en estrategias de marketing digital',
            'nivel': 'Especialista',
            'activo': True
        }
    )
    
    cargo_contador, created = Cargo.objects.get_or_create(
        nombre="Contador Senior",
        defaults={
            'area': area_finanzas,
            'descripcion': 'Contador con experiencia en contabilidad general',
            'nivel': 'Senior',
            'activo': True
        }
    )
    
    # Crear personas
    personas_data = [
        {
            'nombres': 'Juan Carlos',
            'apellido_paterno': 'García',
            'apellido_materno': 'López',
            'tipo_documento': 'DNI',
            'numero_documento': '12345678',
            'fecha_nacimiento': date(1990, 5, 15),
            'sexo': 'M',
            'estado_civil': 'S',
            'email': 'juan.garcia@email.com',
            'celular': '987654321',
            'direccion': 'Av. Principal 123',
            'distrito': 'Miraflores',
            'provincia': 'Lima',
            'departamento': 'Lima'
        },
        {
            'nombres': 'María Elena',
            'apellido_paterno': 'Rodríguez',
            'apellido_materno': 'Silva',
            'tipo_documento': 'DNI',
            'numero_documento': '87654321',
            'fecha_nacimiento': date(1988, 12, 3),
            'sexo': 'F',
            'estado_civil': 'C',
            'email': 'maria.rodriguez@email.com',
            'celular': '912345678',
            'direccion': 'Jr. Los Olivos 456',
            'distrito': 'San Isidro',
            'provincia': 'Lima',
            'departamento': 'Lima'
        },
        {
            'nombres': 'Carlos Alberto',
            'apellido_paterno': 'Mendoza',
            'apellido_materno': 'Vega',
            'tipo_documento': 'DNI',
            'numero_documento': '11223344',
            'fecha_nacimiento': date(1992, 8, 22),
            'sexo': 'M',
            'estado_civil': 'S',
            'email': 'carlos.mendoza@email.com',
            'celular': '955667788',
            'direccion': 'Av. Universitaria 789',
            'distrito': 'La Molina',
            'provincia': 'Lima',
            'departamento': 'Lima'
        },
        {
            'nombres': 'Ana Patricia',
            'apellido_paterno': 'Torres',
            'apellido_materno': 'Herrera',
            'tipo_documento': 'DNI',
            'numero_documento': '55667788',
            'fecha_nacimiento': date(1985, 3, 10),
            'sexo': 'F',
            'estado_civil': 'D',
            'email': 'ana.torres@email.com',
            'celular': '933445566',
            'direccion': 'Calle Las Flores 321',
            'distrito': 'Surco',
            'provincia': 'Lima',
            'departamento': 'Lima'
        },
        {
            'nombres': 'Roberto',
            'apellido_paterno': 'Jiménez',
            'apellido_materno': 'Castro',
            'tipo_documento': 'DNI',
            'numero_documento': '99887766',
            'fecha_nacimiento': date(1991, 11, 28),
            'sexo': 'M',
            'estado_civil': 'S',
            'email': 'roberto.jimenez@email.com',
            'celular': '977889900',
            'direccion': 'Av. Brasil 654',
            'distrito': 'Magdalena',
            'provincia': 'Lima',
            'departamento': 'Lima'
        }
    ]
    
    personas = []
    for data in personas_data:
        persona, created = Persona.objects.get_or_create(
            numero_documento=data['numero_documento'],
            defaults=data
        )
        personas.append(persona)
        print(f"Persona creada: {persona.nombres} {persona.apellido_paterno}")
    
    # Crear CVs
    cvs_data = [
        {
            'persona': personas[0],
            'resumen_profesional': 'Ingeniero de Sistemas con 5 años de experiencia en desarrollo web y aplicaciones móviles. Especializado en Python, Django, React y Node.js. Experiencia en liderazgo de equipos y gestión de proyectos tecnológicos.',
            'objetivo_profesional': 'Busco una posición como Senior Developer donde pueda aplicar mis conocimientos técnicos y liderar equipos de desarrollo para crear soluciones innovadoras.',
            'telefono_profesional': '987654321',
            'email_profesional': 'juan.garcia@email.com',
            'linkedin': 'https://linkedin.com/in/juan-garcia-dev',
            'portfolio': 'https://juangarcia.dev'
        },
        {
            'persona': personas[1],
            'resumen_profesional': 'Marketing Digital con 7 años de experiencia en estrategias de contenido, SEO, SEM y redes sociales. Experiencia en e-commerce y análisis de datos. Certificada en Google Analytics y Facebook Ads.',
            'objetivo_profesional': 'Desarrollar estrategias de marketing digital innovadoras que impulsen el crecimiento de la empresa y mejoren la experiencia del cliente.',
            'telefono_profesional': '912345678',
            'email_profesional': 'maria.rodriguez@email.com',
            'linkedin': 'https://linkedin.com/in/maria-rodriguez-marketing',
            'portfolio': 'https://mariarodriguez-marketing.com'
        },
        {
            'persona': personas[2],
            'resumen_profesional': 'Contador Público con 4 años de experiencia en auditoría, contabilidad general y análisis financiero. Conocimientos en SAP, Excel avanzado y normativas contables peruanas e internacionales.',
            'objetivo_profesional': 'Contribuir al crecimiento financiero de la empresa mediante análisis precisos y estrategias contables eficientes.',
            'telefono_profesional': '955667788',
            'email_profesional': 'carlos.mendoza@email.com',
            'linkedin': 'https://linkedin.com/in/carlos-mendoza-contador'
        },
        {
            'persona': personas[3],
            'resumen_profesional': 'Diseñadora Gráfica con 6 años de experiencia en branding, diseño web y marketing visual. Especializada en Adobe Creative Suite, Figma y diseño UX/UI. Experiencia en agencias y empresas corporativas.',
            'objetivo_profesional': 'Crear diseños impactantes que comuniquen efectivamente la identidad de marca y mejoren la experiencia del usuario.',
            'telefono_profesional': '933445566',
            'email_profesional': 'ana.torres@email.com',
            'linkedin': 'https://linkedin.com/in/ana-torres-diseno',
            'portfolio': 'https://anatorres-design.com'
        },
        {
            'persona': personas[4],
            'resumen_profesional': 'Analista de Recursos Humanos con 3 años de experiencia en reclutamiento, selección y desarrollo de talento. Conocimientos en psicología organizacional, evaluación de competencias y sistemas de gestión de RRHH.',
            'objetivo_profesional': 'Contribuir al desarrollo del capital humano de la organización mediante estrategias efectivas de gestión de talento.',
            'telefono_profesional': '977889900',
            'email_profesional': 'roberto.jimenez@email.com',
            'linkedin': 'https://linkedin.com/in/roberto-jimenez-rrhh'
        }
    ]
    
    cvs = []
    for data in cvs_data:
        cv, created = CV.objects.get_or_create(
            persona=data['persona'],
            defaults=data
        )
        cvs.append(cv)
        print(f"CV creado para: {cv.persona.nombres} {cv.persona.apellido_paterno}")
    
    # Crear convocatorias
    from django.utils import timezone
    from datetime import timedelta
    
    # Usar fechas futuras para evitar problemas de validación
    hoy = timezone.now()
    fecha_futura = hoy + timedelta(days=30)
    
    convocatorias_data = [
        {
            'titulo': 'Desarrollador Full Stack Senior',
            'descripcion': 'Buscamos un desarrollador full stack con experiencia en Python, Django, React y bases de datos. Responsable de desarrollar y mantener aplicaciones web escalables.',
            'cargo': cargo_dev,
            'fecha_apertura': hoy,
            'fecha_cierre': hoy + timedelta(days=30),
            'fecha_inicio_trabajo': fecha_futura.date(),
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': 'Ingeniería de Sistemas o afín, 5+ años de experiencia, conocimientos en Python, Django, React, PostgreSQL, Git',
            'requisitos_deseables': 'Experiencia en liderazgo de equipos, conocimientos en Docker, AWS, metodologías ágiles',
            'experiencia_minima': 5,
            'numero_vacantes': 1,
            'salario_ofrecido': 6500.00,
            'modalidad_trabajo': 'Presencial',
            'ubicacion': 'Lima, Perú'
        },
        {
            'titulo': 'Especialista en Marketing Digital',
            'descripcion': 'Necesitamos un especialista en marketing digital para liderar nuestras estrategias online y mejorar nuestra presencia digital.',
            'cargo': cargo_marketing,
            'fecha_apertura': hoy,
            'fecha_cierre': hoy + timedelta(days=45),
            'fecha_inicio_trabajo': (hoy + timedelta(days=45)).date(),
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': 'Marketing, Comunicaciones o afín, 3+ años de experiencia, conocimientos en Google Analytics, Facebook Ads, SEO, SEM',
            'requisitos_deseables': 'Certificaciones en Google Analytics, Facebook Blueprint, experiencia en e-commerce',
            'experiencia_minima': 3,
            'numero_vacantes': 1,
            'salario_ofrecido': 4500.00,
            'modalidad_trabajo': 'Híbrido',
            'ubicacion': 'Lima, Perú'
        },
        {
            'titulo': 'Contador Senior',
            'descripcion': 'Buscamos un contador senior para manejar la contabilidad general de la empresa y supervisar el equipo contable.',
            'cargo': cargo_contador,
            'fecha_apertura': hoy,
            'fecha_cierre': hoy + timedelta(days=60),
            'fecha_inicio_trabajo': (hoy + timedelta(days=60)).date(),
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': 'Contabilidad o afín, 4+ años de experiencia, conocimientos en SAP, Excel avanzado, normativas contables',
            'requisitos_deseables': 'Certificación CPA, experiencia en auditoría, conocimientos en IFRS',
            'experiencia_minima': 4,
            'numero_vacantes': 1,
            'salario_ofrecido': 5000.00,
            'modalidad_trabajo': 'Presencial',
            'ubicacion': 'Lima, Perú'
        }
    ]
    
    convocatorias = []
    for data in convocatorias_data:
        convocatoria, created = Convocatoria.objects.get_or_create(
            titulo=data['titulo'],
            defaults=data
        )
        convocatorias.append(convocatoria)
        print(f"Convocatoria creada: {convocatoria.titulo}")
    
    # Crear postulaciones
    postulaciones_data = [
        {'persona': personas[0], 'convocatoria': convocatorias[0], 'estado': 'P', 'observaciones': 'Candidato con excelente perfil técnico y experiencia relevante'},
        {'persona': personas[0], 'convocatoria': convocatorias[1], 'estado': 'E', 'observaciones': 'Interesado en transición a marketing digital'},
        {'persona': personas[1], 'convocatoria': convocatorias[1], 'estado': 'A', 'observaciones': 'Perfil ideal para la posición, experiencia sólida en marketing digital'},
        {'persona': personas[2], 'convocatoria': convocatorias[2], 'estado': 'P', 'observaciones': 'Contador con experiencia sólida y conocimientos actualizados'},
        {'persona': personas[3], 'convocatoria': convocatorias[0], 'estado': 'E', 'observaciones': 'Diseñadora interesada en desarrollo frontend'},
        {'persona': personas[4], 'convocatoria': convocatorias[1], 'estado': 'P', 'observaciones': 'Analista de RRHH con interés en marketing digital'}
    ]
    
    for data in postulaciones_data:
        postulacion, created = Postulacion.objects.get_or_create(
            persona=data['persona'],
            convocatoria=data['convocatoria'],
            defaults=data
        )
        print(f"Postulación creada: {postulacion.persona.nombres} -> {postulacion.convocatoria.titulo}")
    
    # Crear formación académica
    formacion_data = [
        {'cv': cvs[0], 'institucion': 'Universidad Nacional de Ingeniería', 'titulo': 'Ingeniero de Sistemas', 'fecha_inicio': date(2008, 3, 1), 'fecha_fin': date(2013, 12, 15), 'estado': 'C', 'descripcion': 'Carrera de Ingeniería de Sistemas con especialización en desarrollo de software'},
        {'cv': cvs[1], 'institucion': 'Universidad de Lima', 'titulo': 'Licenciada en Marketing', 'fecha_inicio': date(2006, 3, 1), 'fecha_fin': date(2011, 12, 15), 'estado': 'C', 'descripcion': 'Carrera de Marketing con enfoque en marketing digital y análisis de mercado'},
        {'cv': cvs[2], 'institucion': 'Universidad del Pacífico', 'titulo': 'Contador Público', 'fecha_inicio': date(2009, 3, 1), 'fecha_fin': date(2014, 12, 15), 'estado': 'C', 'descripcion': 'Carrera de Contabilidad con especialización en auditoría y finanzas'},
        {'cv': cvs[3], 'institucion': 'Instituto Superior Tecnológico Toulouse Lautrec', 'titulo': 'Diseñadora Gráfica', 'fecha_inicio': date(2007, 3, 1), 'fecha_fin': date(2010, 12, 15), 'estado': 'C', 'descripcion': 'Carrera de Diseño Gráfico con especialización en branding y diseño web'},
        {'cv': cvs[4], 'institucion': 'Universidad San Martín de Porres', 'titulo': 'Psicólogo Organizacional', 'fecha_inicio': date(2008, 3, 1), 'fecha_fin': date(2013, 12, 15), 'estado': 'C', 'descripcion': 'Carrera de Psicología con especialización en psicología organizacional y recursos humanos'}
    ]
    
    for data in formacion_data:
        formacion, created = FormacionAcademica.objects.get_or_create(
            cv=data['cv'],
            titulo=data['titulo'],
            defaults=data
        )
        print(f"Formación académica creada: {formacion.titulo} - {formacion.cv.persona.nombres}")
    
    # Crear experiencia laboral
    experiencia_data = [
        {'cv': cvs[0], 'empresa': 'TechCorp Solutions', 'cargo': 'Desarrollador Full Stack', 'fecha_inicio': date(2019, 1, 15), 'fecha_fin': date(2024, 1, 10), 'descripcion': 'Desarrollo de aplicaciones web usando Python, Django, React y PostgreSQL. Liderazgo de equipo de 3 desarrolladores.'},
        {'cv': cvs[1], 'empresa': 'Digital Marketing Agency', 'cargo': 'Especialista en Marketing Digital', 'fecha_inicio': date(2017, 6, 1), 'fecha_fin': date(2024, 1, 5), 'descripcion': 'Desarrollo de estrategias de marketing digital, gestión de campañas publicitarias y análisis de métricas para clientes B2B y B2C.'},
        {'cv': cvs[2], 'empresa': 'Auditores Asociados', 'cargo': 'Contador Senior', 'fecha_inicio': date(2020, 3, 1), 'fecha_fin': date(2024, 1, 12), 'descripcion': 'Supervisión de procesos contables, preparación de estados financieros y coordinación con equipos de auditoría.'},
        {'cv': cvs[3], 'empresa': 'Creative Studio', 'cargo': 'Diseñadora Gráfica Senior', 'fecha_inicio': date(2018, 8, 1), 'fecha_fin': date(2024, 1, 8), 'descripcion': 'Desarrollo de identidades corporativas, diseño web y materiales de marketing para empresas de diversos sectores.'},
        {'cv': cvs[4], 'empresa': 'Recursos Humanos Plus', 'cargo': 'Analista de RRHH', 'fecha_inicio': date(2021, 2, 1), 'fecha_fin': date(2024, 1, 15), 'descripcion': 'Reclutamiento y selección de personal, evaluación de competencias y desarrollo de programas de capacitación.'}
    ]
    
    for data in experiencia_data:
        experiencia, created = ExperienciaLaboral.objects.get_or_create(
            cv=data['cv'],
            empresa=data['empresa'],
            cargo=data['cargo'],
            defaults=data
        )
        print(f"Experiencia laboral creada: {experiencia.cargo} en {experiencia.empresa} - {experiencia.cv.persona.nombres}")
    
    print("\n¡Datos de prueba creados exitosamente!")
    print(f"Total de personas: {Persona.objects.count()}")
    print(f"Total de CVs: {CV.objects.count()}")
    print(f"Total de convocatorias: {Convocatoria.objects.count()}")
    print(f"Total de postulaciones: {Postulacion.objects.count()}")
    print(f"Total de formación académica: {FormacionAcademica.objects.count()}")
    print(f"Total de experiencia laboral: {ExperienciaLaboral.objects.count()}")

if __name__ == '__main__':
    crear_datos_prueba()
