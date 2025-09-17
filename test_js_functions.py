#!/usr/bin/env python
import re

def test_js_functions():
    """Verifica que las funciones JavaScript estén correctamente definidas"""
    
    file_path = r'e:\Datakraft\PRAYAGA\talenthub\master\templates\master\cv.html'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== Verificación de Funciones JavaScript ===")
    
    # Buscar las funciones principales
    functions_to_check = [
        'agregarFormacionAcademica',
        'editarFormacionAcademica', 
        'eliminarFormacionAcademica',
        'guardarFormacionAcademica',
        'agregarCursoEspecializacion',
        'editarCursoEspecializacion',
        'eliminarCursoEspecializacion', 
        'guardarCursoEspecializacion',
        'agregarExperienciaLaboral',
        'editarExperienciaLaboral',
        'eliminarExperienciaLaboral',
        'guardarExperienciaLaboral',
        'showToast'
    ]
    
    for func in functions_to_check:
        if f'function {func}' in content:
            print(f"✅ {func}() - Definida")
        else:
            print(f"❌ {func}() - NO encontrada")
    
    # Verificar sintaxis de JavaScript
    print(f"\n=== Verificación de Sintaxis JavaScript ===")
    
    # Buscar posibles errores de sintaxis
    syntax_issues = []
    
    # Verificar comillas mal escapadas
    if "\\'" in content:
        syntax_issues.append("Comillas simples mal escapadas encontradas")
    
    # Verificar paréntesis desbalanceados
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        syntax_issues.append(f"Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados")
    
    # Verificar llaves desbalanceadas
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        syntax_issues.append(f"Llaves desbalanceadas: {open_braces} abiertas, {close_braces} cerradas")
    
    # Verificar comillas desbalanceadas
    single_quotes = content.count("'")
    if single_quotes % 2 != 0:
        syntax_issues.append("Comillas simples desbalanceadas")
    
    double_quotes = content.count('"')
    if double_quotes % 2 != 0:
        syntax_issues.append("Comillas dobles desbalanceadas")
    
    if syntax_issues:
        print("❌ Problemas de sintaxis encontrados:")
        for issue in syntax_issues:
            print(f"   • {issue}")
    else:
        print("✅ Sintaxis JavaScript correcta")
    
    # Verificar que las variables globales estén definidas
    print(f"\n=== Verificación de Variables Globales ===")
    
    if "const tipoPersona = '{{ tipo_persona }}';" in content:
        print("✅ Variable tipoPersona - Definida correctamente")
    else:
        print("❌ Variable tipoPersona - NO encontrada o mal definida")
        
    if "const personaId = {{ persona.id }};" in content:
        print("✅ Variable personaId - Definida correctamente")
    else:
        print("❌ Variable personaId - NO encontrada o mal definida")
    
    # Verificar que los botones usen las funciones correctas
    print(f"\n=== Verificación de Botones ===")
    
    button_checks = [
        ('onclick="editarFormacionAcademica(', 'Botón editar formación'),
        ('onclick="eliminarFormacionAcademica(', 'Botón eliminar formación'),
        ('onclick="agregarFormacionAcademica()', 'Botón agregar formación'),
    ]
    
    for check, description in button_checks:
        if check in content:
            print(f"✅ {description} - Configurado correctamente")
        else:
            print(f"❌ {description} - NO configurado")
    
    # Verificar estructura de script
    print(f"\n=== Verificación de Estructura de Script ===")
    
    script_tags = content.count('<script>')
    script_close_tags = content.count('</script>')
    
    if script_tags == script_close_tags:
        print(f"✅ Tags de script balanceados: {script_tags} abiertos, {script_close_tags} cerrados")
    else:
        print(f"❌ Tags de script desbalanceados: {script_tags} abiertos, {script_close_tags} cerrados")
    
    print(f"\n=== Recomendaciones ===")
    if not syntax_issues and script_tags == script_close_tags:
        print("✅ El JavaScript parece estar correctamente estructurado")
        print("✅ Si el error persiste, puede ser un problema de orden de carga")
        print("✅ Verificar que jQuery esté cargado antes que este script")
        print("✅ Verificar la consola del navegador para otros errores")
    else:
        print("❌ Hay problemas que deben corregirse antes de que funcione")

if __name__ == "__main__":
    test_js_functions()




