import bpy
import bmesh
import mathutils
import os

path = "d:/Project/webgl2_mesh_render/data/"

# Менять метами YZ
swap_yz_state = True

# Класс для хранения вершины
class Vertex:
    
    def __init__(self, x, y, z, nx, ny, nz, u, v):
        self.x = x
        self.y = y
        self.z = z
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.u = u
        self.v = v
    
    def __str__(self):
        return "v(%.4f, %.4f, %.4f), n(%.4f, %.4f, %.4f), uv(%.4f, %.4f)" % (self.x, self.y, self.z, self.nx, self.ny, self.nz, self.u, self.v)
    
    def __eq__(self, v):
        return self.x == v.x and self.y == v.y and self.z == v.z and self.nx == v.nx and self.ny == v.ny and self.nz == v.nz and self.u == v.u and self.v == v.v
    
# Цикл по объектам в сцене
for obj in bpy.data.objects:
    
    if (obj.type == "MESH"):
        
        file_name = path + obj.name + ".json"
    
        with open(file_name, "w", encoding="utf8", newline="\n") as f:
            
            print("file: %s" % file_name)
            
            # Конвертируем в bmesh 
            bm = bmesh.new()
            bm.from_mesh(obj.data)
                
            # Триангуляция (разбиваем face на триугольники)
            bmesh.ops.triangulate(bm, faces = bm.faces)
            
            # Массив вершин
            vertices = []
            
            # Массив индексов
            indices = []
            
            # Заполняем массивы vertices и indices данными меша
            for face in bm.faces:

                for loop in face.loops:
                    
                    # Получаем значения элементов вершины
                    
                    # Координаты
                    vertex = loop.vert.co

                    # Нормали
                    
                    if loop.face.smooth:
                        normal = loop.vert.normal
                    else:
                        normal = loop.face.normal
                    
                    # Текстурные координаты                    
                    if (bm.loops.layers.uv.active):
                        uv = loop[bm.loops.layers.uv.active].uv
                    else:
                        uv = mathutils.Vector((0.0, 0.0))
                        
                    # Формируем вершину
                    v = Vertex(
                        vertex.x, 
                        vertex.y, 
                        vertex.z,
                        normal.x,
                        normal.y,
                        normal.z,
                        uv.x,
                        uv.y
                    )
                    
                    if swap_yz_state:
                        t = v.y
                        v.y = v.z
                        v.z = t
                        t = v.ny
                        v.ny = v.nz
                        v.nz = t
                    
                    # Получаем индекс вершины, если такой нет, добавляем ее в массив вершин
                    try:
                        index = vertices.index(v)
                    except ValueError:
                        vertices.append(v)
                        index = vertices.index(v)
                        
                    indices.append(index)
                    
            # Формируем JSON данные
            
            json = "{\n"

            # Вершины
            json += "\t\"vertices\":["
            comma = False
            for v in vertices:
                if comma:
                    json += ","
                else:
                    comma = True
                json += "\n\t\t{\"x\":%g, \"y\":%g, \"z\":%g, \"nx\": %g, \"ny\": %g, \"nz\": %g, \"u\": %g, \"v\": %g}" % (v.x, v.y, v.z, v.nx, v.ny, v.nz, v.u, v.v)
            json += "\n\t],\n"
            
            # Индексы                
            json += "\t\"indices\":["
            comma = False
            n = 0
            for i in indices:
                if (comma):
                    json += ","
                else:
                    comma = True
                if n == 0:
                    json += "\n\t\t"
                json += "%d" % i
                n = n + 1
                if n == 3:
                    n = 0
            json += "\n\t]\n"
            
            json += "}"
            
            # Записываем результат в файл и на экран
            f.write(json)
            print(json)
                    
            # Освобождаем память удаляя bmesh 
            bm.free