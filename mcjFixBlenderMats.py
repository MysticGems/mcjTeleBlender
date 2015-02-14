# by mCasualJacques

# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
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

#---------- getTexSlot ----------
def getTexSlot( mat, key, keydot ):
	texSlots = mat.texture_slots
	for texSlot in texSlots:
		if texSlot:
			if ( texSlot.name == key ) or ( texSlot.name.startswith( keydot ) ):
				return( texSlot )
	return 0

#---------- getMap ----------
def getMap( mat, key, keydot ):
	texSlot = getTexSlot( mat, key, keydot )
	if texSlot:
		return( texSlot.texture )
	return 0

#---------- gammaFixMat ----------
def gammaFixMat( mat ):
	color = mat.diffuse_color
	color[0] *= color[0]
	color[1] *= color[1]
	color[2] *= color[2]
	mat.diffuse_color = color
	mat.specular_intensity = 0.02
	mat.use_transparent_shadows = True
		
#---------- fixMat ----------
def fixMat( mat ):
	DMap = getMap( mat, 'D', 'D.' )
	if DMap:
		DMap.use_alpha = False
		mat.alpha = 0
		mat.use_raytrace = False					
	reflMap = getMap( mat, 'refl', 'refl.' )
	if reflMap:
		mat.raytrace_mirror.use = True
		mat.raytrace_mirror.reflect_factor = 1
		mat.mirror_color = mat.diffuse_color
	KaMap = getMap( mat, 'Ka', 'Ka.' )
	if KaMap:
		mat.emit = 1
	KdMap = getMap( mat, 'Kd', 'Kd.' )
	if KdMap:
		KdMap.factor_red = mat.diffuse_color[0]
		KdMap.factor_green = mat.diffuse_color[1]
		KdMap.factor_blue = mat.diffuse_color[2]
	BumpMapSlot = getTexSlot( mat, 'Bump', 'Bump.' )
	if BumpMapSlot:
		BumpMapSlot.normal_factor = 0.05
												
#---------- fixObject ----------
def fixObject( o, bGammaFix ):
	materials = o.material_slots
	for m in materials:
		mat = m.material
		if mat:
			fixMat( mat )
			if bGammaFix:
				gammaFixMat( mat );
		
#---------- fixObjects ----------
def fixObjects( bGammaFix ):
	Scene = bpy.context.scene 
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			fixObject( o, bGammaFix )	

#---------- fixObjectsExcept-----
def fixObjectsExcept( list, bGammaFix ):
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			if( not ( o.name in list ) ):								
				fixObject( o, bGammaFix )	

#---------- setTiling ----------
def setTexTiling( mat, horizontalTiles, horizontalOffset, verticalTiles, verticalOffset ):
	texSlots = mat.texture_slots
	for t in texSlots:
		if hasattr( t, 'offset' ):
			t.offset[0] = horizontalOffset
			t.offset[1] = verticalOffset
			t.scale[0] = horizontalTiles
			t.scale[1] = verticalTiles

#------- setBumpMapStrength -------
def setBumpMapStrength( mat, strength ):
	BumpMapSlot = getTexSlot( mat, 'Bump', 'Bump.' )
	if BumpMapSlot:
		BumpMapSlot.normal_factor = strength 



