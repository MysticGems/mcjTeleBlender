# by mCasualJacques

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
bl_info = {
    "name": "mcjTeleBlender",
    "version": (1, 0),
    "author": "mCasualJacques",
    "blender": (2, 72, 0),
    "description": "DAZ 3D to Blender conversion",
    "category": "DAZ 3D"}

import bpy
#---------- fixMat ----------
def fixMat( mat ):
    color = mat.diffuse_color
    color[0] *= color[0]
    color[1] *= color[1]
    color[2] *= color[2]
    mat.diffuse_color = color
    
#---------- fixObject ----------
def fixObject( o ):
    materials = o.material_slots
    for m in materials:
        mat = m.material
        if mat:
            fixMat( mat )
		
#---------- fixObjects ----------
def fixObjects():
	Scene = bpy.context.scene 
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			fixObject( o )	

#---------- fixObjectsExcept-----
def fixObjectsExcept( list ):
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			if( not ( o.name in list ) ):                
				fixObject( o )	


