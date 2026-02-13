import re

file_path = r'master/templates/master/convocatorias.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace eliminarConvocatoria - simplify it by finding the end of the function's modal-related part
# Find the section that starts the AJAX call for delete, then replace up to that point

pattern_eliminar = r'function eliminarConvocatoria\(id, titulo\) \{[\s\S]*?// Mostrar modal de confirmación\s*\$\(\'#deleteConvocatoriaModal\'\)\.modal\(\'show\'\);'

replacement_eliminar = r"""function eliminarConvocatoria(id, titulo) {
            console.log('Eliminar convocatoria:', id, titulo);
            
            if (confirm(`¿Está seguro de que desea eliminar la convocatoria "${titulo}"?`)) {
                fetch(`/master/convocatorias/${id}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(() => {
                    location.reload();
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al eliminar');
                });
            }"""

content_new = re.sub(pattern_eliminar, replacement_eliminar, content, flags=re.DOTALL)

if content != content_new:
    print('✓ Replaced eliminarConvocatoria')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_new)
    print('Done!')
else:
    print('✗ Pattern not found')
