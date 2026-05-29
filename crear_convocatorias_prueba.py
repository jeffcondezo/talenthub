#!/usr/bin/env python
"""
Script para crear convocatorias de prueba
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talenthub.settings')
django.setup()

from master.models import Convocatoria, Cargo, Area
from django.utils import timezone

def crear_convocatorias_prueba():
    """Crear convocatorias de prueba"""
    
    # Obtener o crear áreas primero
    area_tech, created = Area.objects.get_or_create(
        nombre='Tecnología',
        defaults={
            'descripcion': 'Área de tecnología e innovación'
        }
    )
    if created:
        print(f"Área creada: {area_tech.nombre}")
    else:
        print(f"Área ya existe: {area_tech.nombre}")
    
    area_rh, created = Area.objects.get_or_create(
        nombre='Recursos Humanos',
        defaults={
            'descripcion': 'Área de recursos humanos y gestión del talento'
        }
    )
    if created:
        print(f"Área creada: {area_rh.nombre}")
    else:
        print(f"Área ya existe: {area_rh.nombre}")
    
    area_finanzas, created = Area.objects.get_or_create(
        nombre='Finanzas',
        defaults={
            'descripcion': 'Área de finanzas y contabilidad'
        }
    )
    if created:
        print(f"Área creada: {area_finanzas.nombre}")
    else:
        print(f"Área ya existe: {area_finanzas.nombre}")
    
    area_marketing, created = Area.objects.get_or_create(
        nombre='Marketing',
        defaults={
            'descripcion': 'Área de marketing y comunicaciones'
        }
    )
    if created:
        print(f"Área creada: {area_marketing.nombre}")
    else:
        print(f"Área ya existe: {area_marketing.nombre}")
    
    # Obtener o crear cargos necesarios
    cargo1, created = Cargo.objects.get_or_create(
        nombre='Desarrollador Frontend',
        area=area_tech,
        defaults={
            'descripcion': 'Desarrollador especializado en tecnologías frontend',
            'nivel': 'JUNIOR'
        }
    )
    if created:
        print(f"Cargo creado: {cargo1.nombre}")
    else:
        print(f"Cargo ya existe: {cargo1.nombre}")
    
    cargo2, created = Cargo.objects.get_or_create(
        nombre='Analista de Sistemas',
        area=area_tech,
        defaults={
            'descripcion': 'Analista especializado en análisis y diseño de sistemas',
            'nivel': 'SENIOR'
        }
    )
    if created:
        print(f"Cargo creado: {cargo2.nombre}")
    else:
        print(f"Cargo ya existe: {cargo2.nombre}")
    
    cargo3, created = Cargo.objects.get_or_create(
        nombre='Diseñador UX/UI',
        area=area_marketing,
        defaults={
            'descripcion': 'Diseñador especializado en experiencia de usuario e interfaz',
            'nivel': 'MID'
        }
    )
    if created:
        print(f"Cargo creado: {cargo3.nombre}")
    else:
        print(f"Cargo ya existe: {cargo3.nombre}")
    
    cargo4, created = Cargo.objects.get_or_create(
        nombre='Especialista en RRHH',
        area=area_rh,
        defaults={
            'descripcion': 'Especialista en recursos humanos y gestión del talento',
            'nivel': 'MID'
        }
    )
    if created:
        print(f"Cargo creado: {cargo4.nombre}")
    else:
        print(f"Cargo ya existe: {cargo4.nombre}")
    
    cargo5, created = Cargo.objects.get_or_create(
        nombre='Contador',
        area=area_finanzas,
        defaults={
            'descripcion': 'Contador especializado en contabilidad y finanzas',
            'nivel': 'SENIOR'
        }
    )
    if created:
        print(f"Cargo creado: {cargo5.nombre}")
    else:
        print(f"Cargo ya existe: {cargo5.nombre}")
    
    # Fechas para las convocatorias
    ahora = timezone.now()
    fecha_apertura = ahora
    fecha_cierre = ahora + timedelta(days=30)
    fecha_inicio_trabajo = (ahora + timedelta(days=45)).date()
    
    # Convocatoria 1: Desarrollador Frontend
    convocatoria1, created = Convocatoria.objects.get_or_create(
        titulo='Desarrollador Frontend - Lima',
        defaults={
            'descripcion': '''
            Buscamos un desarrollador frontend con experiencia en React, Vue.js o Angular.
            Responsable de desarrollar interfaces de usuario atractivas y funcionales.
            
            Responsabilidades:
            - Desarrollar componentes reutilizables
            - Optimizar aplicaciones para máxima velocidad y escalabilidad
            - Colaborar con el equipo de diseño y backend
            - Mantener y mejorar código existente
            ''',
            'cargo': cargo1,
            'fecha_apertura': fecha_apertura,
            'fecha_cierre': fecha_cierre,
            'fecha_inicio_trabajo': fecha_inicio_trabajo,
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': '''
            - 2+ años de experiencia en desarrollo frontend
            - Conocimiento sólido en HTML5, CSS3, JavaScript
            - Experiencia con al menos un framework (React, Vue.js, Angular)
            - Conocimiento de Git y control de versiones
            - Inglés intermedio
            ''',
            'requisitos_deseables': '''
            - Experiencia con TypeScript
            - Conocimiento de herramientas de build (Webpack, Vite)
            - Experiencia con testing (Jest, Cypress)
            - Conocimiento de metodologías ágiles
            ''',
            'salario_ofrecido': 4500.00,
            'modalidad_trabajo': 'PRESENCIAL',
            'ubicacion': 'Lima, Perú'
        }
    )
    if created:
        print(f"Convocatoria creada: {convocatoria1.titulo}")
    else:
        print(f"Convocatoria ya existe: {convocatoria1.titulo}")
    
    # Convocatoria 2: Analista de Sistemas
    convocatoria2, created = Convocatoria.objects.get_or_create(
        titulo='Analista de Sistemas - Arequipa',
        defaults={
            'descripcion': '''
            Buscamos un analista de sistemas senior para liderar proyectos de desarrollo
            y análisis de requerimientos.
            
            Responsabilidades:
            - Analizar y documentar requerimientos del negocio
            - Diseñar soluciones técnicas
            - Coordinar con equipos de desarrollo
            - Realizar pruebas de sistemas
            - Capacitar usuarios finales
            ''',
            'cargo': cargo2,
            'fecha_apertura': fecha_apertura,
            'fecha_cierre': fecha_cierre,
            'fecha_inicio_trabajo': fecha_inicio_trabajo,
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': '''
            - 5+ años de experiencia en análisis de sistemas
            - Conocimiento en metodologías de desarrollo (UML, BPMN)
            - Experiencia con bases de datos (SQL Server, Oracle, MySQL)
            - Conocimiento de lenguajes de programación (Java, C#, Python)
            - Inglés avanzado
            ''',
            'requisitos_deseables': '''
            - Certificaciones en análisis de sistemas
            - Experiencia con herramientas de modelado (Visio, Enterprise Architect)
            - Conocimiento de metodologías ágiles (Scrum, Kanban)
            - Experiencia en gestión de proyectos
            ''',
            'salario_ofrecido': 5750.00,
            'modalidad_trabajo': 'PRESENCIAL',
            'ubicacion': 'Arequipa, Perú'
        }
    )
    if created:
        print(f"Convocatoria creada: {convocatoria2.titulo}")
    else:
        print(f"Convocatoria ya existe: {convocatoria2.titulo}")
    
    # Convocatoria 3: Diseñador UX/UI
    convocatoria3, created = Convocatoria.objects.get_or_create(
        titulo='Diseñador UX/UI - Cusco',
        defaults={
            'descripcion': '''
            Buscamos un diseñador UX/UI creativo y orientado al usuario para diseñar
            experiencias digitales excepcionales.
            
            Responsabilidades:
            - Investigar y analizar necesidades de usuarios
            - Crear wireframes, prototipos y mockups
            - Diseñar interfaces intuitivas y atractivas
            - Colaborar con desarrolladores frontend
            - Realizar testing de usabilidad
            ''',
            'cargo': cargo3,
            'fecha_apertura': fecha_apertura,
            'fecha_cierre': fecha_cierre,
            'fecha_inicio_trabajo': fecha_inicio_trabajo,
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': '''
            - 3+ años de experiencia en diseño UX/UI
            - Dominio de herramientas de diseño (Figma, Adobe XD, Sketch)
            - Conocimiento de principios de diseño y usabilidad
            - Experiencia con metodologías de investigación de usuarios
            - Portfolio demostrable
            ''',
            'requisitos_deseables': '''
            - Conocimiento de HTML/CSS básico
            - Experiencia con herramientas de prototipado (InVision, Principle)
            - Conocimiento de accesibilidad web
            - Experiencia en diseño responsive
            - Inglés intermedio
            ''',
            'salario_ofrecido': 4000.00,
            'modalidad_trabajo': 'REMOTO',
            'ubicacion': 'Cusco, Perú'
        }
    )
    if created:
        print(f"Convocatoria creada: {convocatoria3.titulo}")
    else:
        print(f"Convocatoria ya existe: {convocatoria3.titulo}")
    
    # Convocatoria 4: Especialista en RRHH
    convocatoria4, created = Convocatoria.objects.get_or_create(
        titulo='Especialista en RRHH - Lima',
        defaults={
            'descripcion': '''
            Buscamos un especialista en recursos humanos para gestionar procesos
            de selección, capacitación y desarrollo del talento.
            
            Responsabilidades:
            - Gestionar procesos de reclutamiento y selección
            - Coordinar programas de capacitación
            - Administrar políticas de RRHH
            - Realizar evaluaciones de desempeño
            - Mantener relaciones laborales
            ''',
            'cargo': cargo4,
            'fecha_apertura': fecha_apertura,
            'fecha_cierre': fecha_cierre,
            'fecha_inicio_trabajo': fecha_inicio_trabajo,
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': '''
            - 3+ años de experiencia en RRHH
            - Conocimiento en legislación laboral
            - Experiencia en procesos de selección
            - Conocimiento de herramientas de RRHH
            - Excelente comunicación interpersonal
            ''',
            'requisitos_deseables': '''
            - Certificación en RRHH
            - Experiencia con sistemas de gestión de talento
            - Conocimiento de psicología organizacional
            - Experiencia en capacitación y desarrollo
            - Inglés intermedio
            ''',
            'salario_ofrecido': 3500.00,
            'modalidad_trabajo': 'PRESENCIAL',
            'ubicacion': 'Lima, Perú'
        }
    )
    if created:
        print(f"Convocatoria creada: {convocatoria4.titulo}")
    else:
        print(f"Convocatoria ya existe: {convocatoria4.titulo}")
    
    # Convocatoria 5: Contador
    convocatoria5, created = Convocatoria.objects.get_or_create(
        titulo='Contador Senior - Arequipa',
        defaults={
            'descripcion': '''
            Buscamos un contador senior para liderar procesos contables y financieros
            de la organización.
            
            Responsabilidades:
            - Liderar procesos contables y financieros
            - Preparar estados financieros
            - Gestionar auditorías
            - Supervisar equipo contable
            - Cumplir normativas fiscales
            ''',
            'cargo': cargo5,
            'fecha_apertura': fecha_apertura,
            'fecha_cierre': fecha_cierre,
            'fecha_inicio_trabajo': fecha_inicio_trabajo,
            'estado': 'PUBLICADA',
            'tipo': 'EXTERNA',
            'requisitos_minimos': '''
            - 5+ años de experiencia en contabilidad
            - Título profesional en Contabilidad
            - Conocimiento de NIIF y NIC
            - Experiencia con software contable
            - Conocimiento de normativas fiscales
            ''',
            'requisitos_deseables': '''
            - Certificación CPA o similar
            - Experiencia en auditoría
            - Conocimiento de sistemas ERP
            - Experiencia en gestión de equipos
            - Inglés intermedio
            ''',
            'salario_ofrecido': 5000.00,
            'modalidad_trabajo': 'PRESENCIAL',
            'ubicacion': 'Arequipa, Perú'
        }
    )
    if created:
        print(f"Convocatoria creada: {convocatoria5.titulo}")
    else:
        print(f"Convocatoria ya existe: {convocatoria5.titulo}")

def main():
    """Función principal"""
    print("Creando convocatorias de prueba...")
    print("=" * 50)
    
    crear_convocatorias_prueba()
    
    print("\n" + "=" * 50)
    print("Convocatorias creadas!")
    print(f"Total convocatorias: {Convocatoria.objects.count()}")

if __name__ == '__main__':
    main()
