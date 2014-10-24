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

import bpy

dictionary = [
	['ShaderNodeBackground', 'BACKGROUND'],
	['ShaderNodeMapping', 'MAPPING'],
	['ShaderNodeTexImage', 'TEX_IMAGE'],
	['ShaderNodeTexCoord', 'TEX_COORD'],
	['ShaderNodeTexEnvironment', 'TEX_ENVIRONMENT' ]
]

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------	
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

#---------- socketOccupied ----------
def socketOccupied( links, socket ):
    for link in links:
        if( socket == link.to_socket ):
            return True
    return False
        
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def addHorizonColor( r, g, b, strength ):
	world = bpy.data.worlds[0]
	world.use_nodes = True
	tree = world.node_tree
	nodes = tree.nodes
	back = 0;
	for node in nodes:
		if( node.type in ['ShaderNodeBackground','BACKGROUND'] ):
			back = node
	if back:
			back.inputs[0].default_value = [ r, g, b, 1 ]
			back.inputs[1].default_value = strength

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def addHorizonColorBlender( r, g, b, strength ):
	world = bpy.context.scene.world
	world.horizon_color[0] = r
	world.horizon_color[1] = g
	world.horizon_color[2] = b
	world.light_settings.use_environment_light = True
	world.light_settings.environment_energy = strength
	world.light_settings.environment_color = 'SKY_COLOR'

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def addSky( image, strength ):
	world = bpy.data.worlds[0]
	world.use_nodes = True
	tex = bpy.data.textures.new( 'texture', type = 'IMAGE' )
	tex.image = bpy.data.images.load( image )
	tree = world.node_tree
	nodes = tree.nodes
	links = tree.links
	back = 0;
	for node in nodes:
		if node.type in ['ShaderNodeBackground', 'BACKGROUND']:
			back = node
	if back:
		#if back.type == 'ShaderNodeBackground':
		#shaderLang = 0
		#else:
		shaderLang = 1
		ox = back.location.x
		oy = back.location.y
		texEnv = nodes.new( trad( 'ShaderNodeTexEnvironment') )
		texEnv.location = ( ox - 300, oy )
		texEnv.image = tex.image
		back.inputs[1].default_value = strength  
		links.new( texEnv.outputs[0], back.inputs[0] )
		mappingNode = nodes.new(trad( 'ShaderNodeMapping'))
		mappingNode.location = ( texEnv.location.x - 270, texEnv.location.y )
		links.new( mappingNode.outputs['Vector'], texEnv.inputs['Vector'] )
		texCoordNode = nodes.new( trad( 'ShaderNodeTexCoord') )
		texCoordNode.location = ( mappingNode.location.x - 270, mappingNode.location.y )
		links.new( texCoordNode.outputs['Generated'], mappingNode.inputs['Vector'] )
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def addSkyBlender( image, strength ):
    world = bpy.context.scene.world
    world.light_settings.use_environment_light = True
    world.light_settings.environment_energy = strength
    world.light_settings.environment_color = 'SKY_TEXTURE'
    tex = bpy.data.textures.new( 'texture', type = 'IMAGE' )
    tex.image = bpy.data.images.load( image )
    world.active_texture = tex
    slot = world.texture_slots[world.active_texture_index]
    slot.use_map_blend = True
    slot.use_map_horizon = True
    slot.use_map_zenith_up = True
    slot.use_map_zenith_down = True
