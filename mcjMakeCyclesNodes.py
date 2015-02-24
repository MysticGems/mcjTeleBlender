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

import bpy, math
import struct
from bpy.props import StringProperty
import os
import io_scene_obj.import_obj
from bpy_extras.io_utils import axis_conversion

# this was removed because it caused problems with 
# Blender 2.66.3's compositing nodes display
# ( but could be handled by launching a 
# short even-if-incomplete render
# bpy.context.scene.use_nodes = True

#----- getShader ------

# Selects a shader based on common DAZ surfaces
# Defaults to a plain diffuse

surfaces = [
	[ 'defaultMat' , 'Skin Shader' ],
	[ 'Cornea' , 'ShaderNodeBsdfGlass' ],
	[ 'Ears' , 'Skin Shader' ],
#	[ 'Eyelashes' , 'Skin Shader' ],
	[ 'EyeReflection' , 'ShaderNodeBsdfTransparent' ],
	[ 'Face' , 'Skin Shader' ],
	[ 'Feet' , 'Skin Shader' ],
#	[ 'Fingernails' , 'Skin Shader' ],
	[ 'Forearms' , 'Skin Shader' ],
	[ 'Gums' , 'Skin Shader' ],
	[ 'Hands' , 'Skin Shader' ],
	[ 'Head' , 'Skin Shader' ],
	[ 'Hips' , 'Skin Shader' ],
	[ 'InnerMouth' , 'Skin Shader' ],
	[ 'Irises' , 'Eye Shader' ],
	[ 'Lacrimals' , 'Skin Shader' ],
	[ 'Legs' , 'Skin Shader' ],
	[ 'Lips' , 'Skin Shader' ],
	[ 'Neck' , 'Skin Shader' ],
	[ 'Nipples' , 'Skin Shader' ],
	[ 'Nostrils' , 'Skin Shader' ],
	[ 'Pupils' , 'Eye Shader' ],
	[ 'Sclera' , 'Eye Shader' ],
	[ 'Shoulders' , 'Skin Shader' ],
	[ 'Tear' , 'ShaderNodeBsdfGlass' ],
	[ 'Teeth' , 'Skin Shader' ],
#	[ 'Toenails' , 'Skin Shader' ],
	[ 'Tongue' , 'Skin Shader' ],
	[ 'Torso' , 'Skin Shader' ],
	[ 'Base' , 'Hair Shader' ],
	[ 'Hair' , 'Hair Shader' ]
]

def getShader( str ):
	for duet in surfaces:
		if duet[0] in str:
			return duet[1]
	return 'ShaderNodeBsdfDiffuse'
	
#-------- trad -----------

dictionary = [
	['ShaderNodeOutputMaterial', 'OUTPUT_MATERIAL'],
	['ShaderNodeBsdfDiffuse', 'BSDF_DIFFUSE'],
	['ShaderNodeMixRGB', 'MIX_RGB'],
	['ShaderNodeBsdfGlossy', 'BSDF_GLOSSY'],
	['ShaderNodeAddShader', 'ADD_SHADER'],
	['ShaderNodeEmission', 'EMISSION'],
	['ShaderNodeTexImage', 'TEX_IMAGE'],
	['ShaderNodeMath', 'MATH'],
	['ShaderNodeMixShader', 'MIX_SHADER'],
	['ShaderNodeGroup', ''],
	['ShaderNodeBsdfGlass', ''],
	['ShaderNodeBsdfTransparent', 'BSDF_TRANSPARENT'],
	['ShaderNodeFresnel', 'INPUT_FRESNEL']
]

def trad( str ):
	ver = bpy.app.version;
	if( ( ver[0] == 2 ) and ( ver [1] > 66 ) ):
		shaderLang = 0
	elif( ( ver[0] == 2 ) and ( ver [1] == 66 ) and ( ver[2] > 1 ) ):
		shaderLang = 0
	else:
		shaderLang = 1
	for duet in dictionary:
		if str in duet:
			return( duet[shaderLang] )

#---------- getMap ----------
def getMap( mat, key, keydot ):
	texSlots = mat.texture_slots
	for t in texSlots:
		if t:
			if ( t.name == key ) or ( t.name.startswith(keydot) ):
				return( t.texture )
	return 0

#---------- fixMat ----------
def fixMat( mat, Glossfactor, GlossRough, mtlname ):
	diffuseColor = mat.diffuse_color
	specularColor = mat.specular_color
	opacityStrength = mat.alpha
	tree = mat.node_tree
	if not tree:
		mat.use_nodes = True
	tree = mat.node_tree
	if not tree:
		return
	nodes = tree.nodes
	#we only process trees created by default
	if len(nodes) != 2: 
		return
	if( nodes[0].type in ["OUTPUT_MATERIAL","ShaderNodeOutputMaterial"] ):
		outNode = nodes[0]
		bsdfNode = nodes[1]
		if( bsdfNode.type not in ["BSDF_DIFFUSE","ShaderNodeBsdfDiffuse"] ):
			return
	else:
		outNode = nodes[1]
		if( outNode.type not in ["OUTPUT_MATERIAL","ShaderNodeOutputMaterial"] ):
			return
		bsdfNode = nodes[0]
		if( bsdfNode.type not in ["BSDF_DIFFUSE","ShaderNodeBsdfDiffuse"] ):
			return

	ox = outNode .location.x
	oy = outNode .location.y
	links = tree.links
	bsdfNode.location = ( ox - 600, oy )

	# RGB mix node (for tint)
	mixNode = nodes.new(trad( 'ShaderNodeMixRGB'))
	mixNode.location = ( ox - 900, oy )
	mixNode.inputs[1].default_value = [ 1, 1, 1, 1 ]
	mixNode.inputs[2].default_value = [ diffuseColor[0], diffuseColor[1], diffuseColor[2], 1 ]
	mixNode.blend_type = 'MULTIPLY'
	mixNode.inputs[0].default_value = 1.0
# 	
# 	glossNode = nodes.new(trad( 'ShaderNodeBsdfGlossy'))
# 	glossNode .location = ( ox - 600, oy - 100 )

	shader = getShader( mtlname )

	if "ShaderNode" in shader:
		newNode = nodes.new(trad(shader))
		nodes.remove( bsdfNode )
		bsdfNode = newNode
		if 'ShaderNodeBsdfGlass' == shader:
			newNode.inputs[2].default_value = 1.376
	else:
		# Create a shader group node; this must already be in the blend file
		groupNode = nodes.new( trad('ShaderNodeGroup') )
		groupNode.node_tree = bpy.data.node_groups[getShader( mtlname )]
		nodes.remove( bsdfNode )
		bsdfNode = groupNode
	
	bsdfNode .location = ( ox - 400, oy )
	# Link it to output
	links.new( bsdfNode.outputs[0], outNode.inputs[0] )
	
# 	glossNode.inputs[0].default_value = [1,1,1,1]
# 	glossNode.inputs[1].default_value = GlossRough 
# 	addNode = nodes.new(trad( 'ShaderNodeMixShader'))
# 	addNode .location = ( ox - 300, oy )
	links.new( mixNode.outputs[0], bsdfNode.inputs[0] )
# 	links.new( bsdfNode.outputs[0], addNode.inputs[1] )
# 	links.new( glossNode.outputs[0], addNode.inputs[2] )
# 	links.new( addNode.outputs[0], outNode.inputs[0] ) 

# Disregard ambient color for now
# 	KaMap = getMap( mat, 'Ka', 'Ka.' )
# 	if KaMap:
# 		emNode = nodes.new(trad( 'ShaderNodeEmission'))
# 		emNode.location = ( ox - 750, oy + 300 )
# 		emNode.inputs[1].default_value = 100
# 		links.new( mixNode.outputs[0], emNode.inputs[0] )
# 		links.new( emNode.outputs[0], outNode.inputs[0] )
# 		nodes.remove(bsdfNode)
# 		bsdfNode = emNode
		
# Disregard reflective map for now
# 	reflMap = getMap( mat, 'refl', 'refl.' )
# 	if reflMap:
# 		print( "got a mirror" )
# 		glossNode.distribution = "SHARP"
# 		glossNode.inputs[0].default_value = [specularColor[0],specularColor[1],specularColor[2],1]
# 
# Disregard specular color for now
# 	KsMap = getMap( mat, 'Ks', 'Ks.' )
# 	if KsMap:
# 		texNode = nodes.new(trad( 'ShaderNodeTexImage'))
# 		texNode.location = ( ox - 1200, oy - 100 )
# 		texNode.image = KsMap.image
# 		mulNode = nodes.new(trad( 'ShaderNodeMath'))
# 		mulNode.operation = 'MULTIPLY'
# 		mulNode.inputs[1].default_value = 0.1
# 		mulNode.location = ( ox - 900, oy - 100 )
# 		links.new( texNode.outputs[0], mulNode.inputs[0] )
# 		links.new( mulNode.outputs[0], groupNode.inputs[0] )

	if 'ShaderNodeBsdfGlass' != shader:
		# Add the diffuse map to the group node color input
		KdMap = getMap( mat, 'Kd', 'Kd.' )
		if KdMap:
			texNode = nodes.new(trad( 'ShaderNodeTexImage'))
			texNode.location = ( ox - 1200, oy )
			texNode.image = KdMap.image
			links.new( texNode.outputs[0], mixNode.inputs[1] )
			
		if 'ShaderNodeBsdfTransparent' != shader:
			# Use the transparency (dissolve) map
			DMap = getMap( mat, 'D', 'D.' )
			if( ( opacityStrength < 1 ) or ( DMap ) ):
				mixNode = nodes.new(trad( 'ShaderNodeMixShader'))
				mixNode .location = ( ox - 150, oy + 150 )
				if( DMap ):
					texNodeD = nodes.new(trad( 'ShaderNodeTexImage'))
					texNodeD.location = ( ox - 400, oy + 320)
					texNodeD.image = DMap.image
					links.new( texNodeD.outputs[0], mixNode.inputs[0] )
				elif( opacityStrength < 1 ):
					mixNode.inputs[0].default_value = opacityStrength
				xpaNode = nodes.new(trad( 'ShaderNodeBsdfTransparent'))
				xpaNode .location = ( ox - 400, oy + 100 )
				outNode .location.x = outNode .location.x + 200
		#		addNode .location.x = addNode .location.x - 100
				links.new( xpaNode.outputs[0], mixNode.inputs[1] )
				links.new( bsdfNode.outputs[0], mixNode.inputs[2] )
				links.new( mixNode.outputs[0], outNode.inputs[0] )

	# Use bump map
	BumpMap = getMap( mat, 'Bump', 'Bump.' )
	if BumpMap:
		texNode = nodes.new(trad( 'ShaderNodeTexImage'))
		texNode.location = ( ox - 600, oy - 300 ) 
		texNode.image = BumpMap.image
		mulNode = nodes.new(trad( 'ShaderNodeMath'))
		mulNode.location = ( ox - 300, oy - 200 )
		mulNode.operation = "MULTIPLY"
		mulNode.inputs[0].default_value = 0.003
		links.new( texNode.outputs[0], mulNode.inputs[1] )
		links.new( mulNode.outputs[0], outNode.inputs[2] )

#---------- fixObject ----------
def fixObject( o, Glossfactor, GlossRough ):
	materials = o.material_slots
	for m in materials:
		mat = m.material
		if mat:
			fixMat( mat, Glossfactor, GlossRough, mat.name )
		
#---------- fixObjects ----------
def fixObjects():
	try:
		Glossfactor = bpy.types.Scene.Glossfactor
	except AttributeError:
		Glossfactor = 0.05
	try:
		GlossRough = bpy.types.Scene.GlossRough
	except AttributeError:
		GlossRough = 0.20
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			fixObject( o, Glossfactor, GlossRough )	

#---------- fixObjectsExcept-----
def fixObjectsExcept( list ):
	try:
		Glossfactor = bpy.types.Scene.Glossfactor
	except AttributeError:
		Glossfactor = 0.05
	try:
		GlossRough = bpy.types.Scene.GlossRough
	except AttributeError:
		GlossRough = 0.20
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			if( not ( o.name in list ) ):				
				fixObject( o, Glossfactor, GlossRough )	
