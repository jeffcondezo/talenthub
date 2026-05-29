#!/usr/bin/env python
"""
Script para cargar departamentos, provincias y distritos del Perú
Basado en datos oficiales del INEI
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talenthub.settings')
django.setup()

from master.models import Departamento, Provincia, Distrito

def cargar_departamentos():
    """Cargar departamentos del Perú"""
    departamentos_data = [
        ('01', 'Amazonas'),
        ('02', 'Áncash'),
        ('03', 'Apurímac'),
        ('04', 'Arequipa'),
        ('05', 'Ayacucho'),
        ('06', 'Cajamarca'),
        ('07', 'Callao'),
        ('08', 'Cusco'),
        ('09', 'Huancavelica'),
        ('10', 'Huánuco'),
        ('11', 'Ica'),
        ('12', 'Junín'),
        ('13', 'La Libertad'),
        ('14', 'Lambayeque'),
        ('15', 'Lima'),
        ('16', 'Loreto'),
        ('17', 'Madre de Dios'),
        ('18', 'Moquegua'),
        ('19', 'Pasco'),
        ('20', 'Piura'),
        ('21', 'Puno'),
        ('22', 'San Martín'),
        ('23', 'Tacna'),
        ('24', 'Tumbes'),
        ('25', 'Ucayali'),
    ]
    
    for codigo, nombre in departamentos_data:
        departamento, created = Departamento.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre}
        )
        if created:
            print(f"Departamento creado: {nombre}")
        else:
            print(f"Departamento ya existe: {nombre}")

def cargar_provincias():
    """Cargar provincias principales del Perú"""
    provincias_data = [
        # Lima
        ('1501', 'Lima', '15'),
        ('1507', 'Callao', '15'),
        ('1502', 'Barranca', '15'),
        ('1503', 'Cajatambo', '15'),
        ('1504', 'Canta', '15'),
        ('1505', 'Cañete', '15'),
        ('1506', 'Huaral', '15'),
        ('1508', 'Huarochirí', '15'),
        ('1509', 'Huaura', '15'),
        ('1510', 'Oyón', '15'),
        ('1511', 'Yauyos', '15'),
        
        # Arequipa
        ('0401', 'Arequipa', '04'),
        ('0402', 'Camaná', '04'),
        ('0403', 'Caravelí', '04'),
        ('0404', 'Castilla', '04'),
        ('0405', 'Caylloma', '04'),
        ('0406', 'Condesuyos', '04'),
        ('0407', 'Islay', '04'),
        ('0408', 'La Uniòn', '04'),
        
        # Cusco
        ('0801', 'Cusco', '08'),
        ('0802', 'Acomayo', '08'),
        ('0803', 'Anta', '08'),
        ('0804', 'Calca', '08'),
        ('0805', 'Canas', '08'),
        ('0806', 'Canchis', '08'),
        ('0807', 'Chumbivilcas', '08'),
        ('0808', 'Espinar', '08'),
        ('0809', 'La Convención', '08'),
        ('0810', 'Paruro', '08'),
        ('0811', 'Paucartambo', '08'),
        ('0812', 'Quispicanchi', '08'),
        ('0813', 'Urubamba', '08'),
        
        # La Libertad
        ('1301', 'Trujillo', '13'),
        ('1302', 'Ascope', '13'),
        ('1303', 'Bolívar', '13'),
        ('1304', 'Chepén', '13'),
        ('1305', 'Gran Chimú', '13'),
        ('1306', 'Julcán', '13'),
        ('1307', 'Otuzco', '13'),
        ('1308', 'Pacasmayo', '13'),
        ('1309', 'Pataz', '13'),
        ('1310', 'Sánchez Carrión', '13'),
        ('1311', 'Santiago de Chuco', '13'),
        ('1312', 'Virú', '13'),
        
        # Piura
        ('2001', 'Piura', '20'),
        ('2002', 'Ayabaca', '20'),
        ('2003', 'Huancabamba', '20'),
        ('2004', 'Morropón', '20'),
        ('2005', 'Paita', '20'),
        ('2006', 'Sullana', '20'),
        ('2007', 'Talara', '20'),
        ('2008', 'Sechura', '20'),
    ]
    
    for codigo, nombre, departamento_codigo in provincias_data:
        try:
            departamento = Departamento.objects.get(codigo=departamento_codigo)
            provincia, created = Provincia.objects.get_or_create(
                codigo=codigo,
                departamento=departamento,
                defaults={'nombre': nombre}
            )
            if created:
                print(f"Provincia creada: {nombre} - {departamento.nombre}")
            else:
                print(f"Provincia ya existe: {nombre} - {departamento.nombre}")
        except Departamento.DoesNotExist:
            print(f"Departamento no encontrado para provincia: {nombre}")

def cargar_distritos():
    """Cargar distritos principales del Perú"""
    distritos_data = [
        # Lima - Lima
        ('150101', 'Lima', '1501'),
        ('150102', 'Ancón', '1501'),
        ('150103', 'Ate', '1501'),
        ('150104', 'Barranco', '1501'),
        ('150105', 'Breña', '1501'),
        ('150106', 'Carabayllo', '1501'),
        ('150107', 'Chaclacayo', '1501'),
        ('150108', 'Chorrillos', '1501'),
        ('150109', 'Cieneguilla', '1501'),
        ('150110', 'Comas', '1501'),
        ('150111', 'El Agustino', '1501'),
        ('150112', 'Independencia', '1501'),
        ('150113', 'Jesús María', '1501'),
        ('150114', 'La Molina', '1501'),
        ('150115', 'La Victoria', '1501'),
        ('150116', 'Lince', '1501'),
        ('150117', 'Los Olivos', '1501'),
        ('150118', 'Lurigancho', '1501'),
        ('150119', 'Lurín', '1501'),
        ('150120', 'Magdalena del Mar', '1501'),
        ('150121', 'Miraflores', '1501'),
        ('150122', 'Pachacámac', '1501'),
        ('150123', 'Pucusana', '1501'),
        ('150124', 'Pueblo Libre', '1501'),
        ('150125', 'Puente Piedra', '1501'),
        ('150126', 'Punta Hermosa', '1501'),
        ('150127', 'Punta Negra', '1501'),
        ('150128', 'Rímac', '1501'),
        ('150129', 'San Bartolo', '1501'),
        ('150130', 'San Borja', '1501'),
        ('150131', 'San Isidro', '1501'),
        ('150132', 'San Juan de Lurigancho', '1501'),
        ('150133', 'San Juan de Miraflores', '1501'),
        ('150134', 'San Luis', '1501'),
        ('150135', 'San Martín de Porres', '1501'),
        ('150136', 'San Miguel', '1501'),
        ('150137', 'Santa Anita', '1501'),
        ('150138', 'Santa María del Mar', '1501'),
        ('150139', 'Santa Rosa', '1501'),
        ('150140', 'Santiago de Surco', '1501'),
        ('150141', 'Surquillo', '1501'),
        ('150142', 'Villa El Salvador', '1501'),
        ('150143', 'Villa María del Triunfo', '1501'),
        
        # Callao
        ('150701', 'Callao', '1507'),
        ('150702', 'Bellavista', '1507'),
        ('150703', 'Carmen de la Legua Reynoso', '1507'),
        ('150704', 'La Perla', '1507'),
        ('150705', 'La Punta', '1507'),
        ('150706', 'Ventanilla', '1507'),
        
        # Arequipa - Arequipa
        ('040101', 'Arequipa', '0401'),
        ('040102', 'Alto Selva Alegre', '0401'),
        ('040103', 'Cayma', '0401'),
        ('040104', 'Cerro Colorado', '0401'),
        ('040105', 'Characato', '0401'),
        ('040106', 'Chiguata', '0401'),
        ('040107', 'Jacobo Hunter', '0401'),
        ('040108', 'La Joya', '0401'),
        ('040109', 'Mariano Melgar', '0401'),
        ('040110', 'Miraflores', '0401'),
        ('040111', 'Mollebaya', '0401'),
        ('040112', 'Paucarpata', '0401'),
        ('040113', 'Pocsi', '0401'),
        ('040114', 'Polobaya', '0401'),
        ('040115', 'Quequeña', '0401'),
        ('040116', 'Sabandia', '0401'),
        ('040117', 'Sachaca', '0401'),
        ('040118', 'San Juan de Siguas', '0401'),
        ('040119', 'San Juan de Tarucani', '0401'),
        ('040120', 'Santa Isabel de Siguas', '0401'),
        ('040121', 'Santa Rita de Siguas', '0401'),
        ('040122', 'Socabaya', '0401'),
        ('040123', 'Tiabaya', '0401'),
        ('040124', 'Uchumayo', '0401'),
        ('040125', 'Vitor', '0401'),
        ('040126', 'Yanahuara', '0401'),
        ('040127', 'Yarabamba', '0401'),
        ('040128', 'Yura', '0401'),
        
        # Cusco - Cusco
        ('080101', 'Cusco', '0801'),
        ('080102', 'Ccorca', '0801'),
        ('080103', 'Poroy', '0801'),
        ('080104', 'San Jerónimo', '0801'),
        ('080105', 'San Sebastian', '0801'),
        ('080106', 'Santiago', '0801'),
        ('080107', 'Saylla', '0801'),
        ('080108', 'Wanchaq', '0801'),
        
        # La Libertad - Trujillo
        ('130101', 'Trujillo', '1301'),
        ('130102', 'El Porvenir', '1301'),
        ('130103', 'Florencia de Mora', '1301'),
        ('130104', 'Huanchaco', '1301'),
        ('130105', 'La Esperanza', '1301'),
        ('130106', 'Laredo', '1301'),
        ('130107', 'Moche', '1301'),
        ('130108', 'Poroto', '1301'),
        ('130109', 'Salaverry', '1301'),
        ('130110', 'Simbal', '1301'),
        ('130111', 'Victor Larco Herrera', '1301'),
        
        # Piura - Piura
        ('200101', 'Piura', '2001'),
        ('200102', 'Castilla', '2001'),
        ('200103', 'Catacaos', '2001'),
        ('200104', 'Cura Mori', '2001'),
        ('200105', 'El Tallán', '2001'),
        ('200106', 'La Arena', '2001'),
        ('200107', 'La Unión', '2001'),
        ('200108', 'Las Lomas', '2001'),
        ('200109', 'Tambo Grande', '2001'),
        ('200110', 'Veintiseis de Octubre', '2001'),
    ]
    
    for codigo, nombre, provincia_codigo in distritos_data:
        try:
            provincia = Provincia.objects.get(codigo=provincia_codigo)
            distrito, created = Distrito.objects.get_or_create(
                codigo=codigo,
                provincia=provincia,
                defaults={'nombre': nombre}
            )
            if created:
                print(f"Distrito creado: {nombre} - {provincia.nombre}")
            else:
                print(f"Distrito ya existe: {nombre} - {provincia.nombre}")
        except Provincia.DoesNotExist:
            print(f"Provincia no encontrada para distrito: {nombre}")

def main():
    """Función principal"""
    print("Cargando datos de ubicaciones del Perú...")
    print("=" * 50)
    
    print("\n1. Cargando departamentos...")
    cargar_departamentos()
    
    print("\n2. Cargando provincias...")
    cargar_provincias()
    
    print("\n3. Cargando distritos...")
    cargar_distritos()
    
    print("\n" + "=" * 50)
    print("Carga completada!")
    print(f"Total departamentos: {Departamento.objects.count()}")
    print(f"Total provincias: {Provincia.objects.count()}")
    print(f"Total distritos: {Distrito.objects.count()}")

if __name__ == '__main__':
    main()
