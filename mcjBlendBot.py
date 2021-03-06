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
import sys
import random
import io_scene_obj.import_obj
from bpy_extras.io_utils import axis_conversion
import mcjMakeCyclesNodes
import mcjFixBlenderMats
import mcjUseMatLib
import mcjGammaFix
import mcjAddSky
import mcjMatsFromFilename
import mcjAddMappersToTexImgs

#----- getShader ------

# Selects a shader based on common DAZ surfaces
# Defaults to a plain diffuse

surfaces = [
	[ 'Labia_Minora', 'Skin Shader' ],
	[ 'Anus', 'Skin Shader' ],
	[ 'Genitalia' , 'Skin Shader' ],
	[ 'defaultMat' , 'Skin Shader' ],
	[ 'Ears' , 'Skin Shader' ],
	[ 'Face' , 'Skin Shader' ],
	[ 'Feet' , 'Skin Shader' ],
	[ 'Arms', 'Skin Shader' ],
	[ 'Fingernails' , 'Skin Shader' ],
	[ 'Forearms' , 'Skin Shader' ],
	[ 'Hands' , 'Skin Shader' ],
	[ 'Head' , 'Skin Shader' ],
	[ 'Hips' , 'Skin Shader' ],
	[ 'Lacrimals' , 'Skin Shader' ],
	[ 'Legs' , 'Skin Shader' ],
	[ 'Neck' , 'Skin Shader' ],
	[ 'Nipples' , 'Skin Shader' ],
	[ 'Nostrils' , 'Skin Shader' ],
	[ 'Shoulders' , 'Skin Shader' ],
	[ 'Toenails' , 'Skin Shader' ],
	[ 'Torso' , 'Skin Shader' ],
	[ 'Vagina&Rectum', 'Skin Shader' ]
]

def getShader( str ):
	for duet in surfaces:
		if duet[0] in str:
			return duet[1]
	return 'PBR Roughness'
	

#-------------------------------------------------------------------------------		
# when daz studio finds a name that already exists in the mtl file
# it appends the node label (which sometimes differs from the node name
# default ----> default_mcjA3BodyconR_(2)
#-------------------------------------------------------------------------------	
def intelliFindMat( obj, nodeName, matName ):
	try:
		if matName in obj.material_slots:
			return( obj.material_slots[matName] )
		longname = matName + "_" + nodeName
		if longname in obj.material_slots:
			return( obj.material_slots[longname] )
		for slt in obj.material_slots:
			if slt.name.startswith( matName ):
				return( slt )
	except AttributeError:
		print( '	' + nodeName + ' has no material slots' )
	return( 0 )

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------	
def intelliFindObj( nodeName ): 
	if nodeName in bpy.data.objects:
		return( bpy.data.objects[nodeName] )
	for o in bpy.data.objects:
		if o.name.startswith( nodeName ):
			return( o )
	return( 0 )	

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------	
def setTiling( nodeName, matName, horizontalTiles, horizontalOffset, verticalTiles, verticalOffset ):
	obj = intelliFindObj( nodeName )
	if obj:
		mtrslt = intelliFindMat( obj, nodeName, matName )
		if mtrslt:
			mat = mtrslt.material;
			tree = mat.node_tree
			if( not tree ):
				mcjFixBlenderMats.setTexTiling( mat, horizontalTiles, horizontalOffset, verticalTiles, verticalOffset )
			else:
				nodes = tree.nodes
				for coord in nodes :
					if( coord.type in ['ShaderNodeMapping', 'MAPPING'] ):
						coord.scale.x = horizontalTiles
						coord.translation.x = horizontalOffset
						coord.scale.y = verticalTiles
						coord.translation.y = verticalOffset
		else:
			print( "unable to find material named " + matName )
	else:
		print( "unable to find object named " + nodeName )
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------	
def setBumpMapStrength( nodeName, matName, strength ):
	obj = intelliFindObj( nodeName )
	if obj:
		mtrslt	= intelliFindMat( obj, nodeName, matName )
		if mtrslt:
			mat = mtrslt.material;
			tree = mat.node_tree
			if( not tree ):
				mcjFixBlenderMats.setBumpMapStrength( mat, strength )
			else:
				nodes = tree.nodes
				for outputNode in nodes :
					if( outputNode.type in ['ShaderNodeOutputMaterial', 'OUTPUT_MATERIAL'] ):
						in2links = outputNode.inputs[2].links
						if( in2links ):
							in2links0 = in2links[0]
							if( in2links0 ):
								multnode = in2links0.from_node
								if multnode:
									multnode.inputs[0].default_value = strength;
		else:
			print( "unable to find material named " + matName )
	else:
		print( "unable to find object named " + nodeName )
				
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setSmooth(bSmooth):
	bpy.types.Scene.bSmooth= bpy.props.BoolProperty()
	bpy.types.Scene.bSmooth= bSmooth

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setEdgeSplit(bEdgeSplit ):
	bpy.types.Scene.bEdgeSplit = bpy.props.BoolProperty()
	bpy.types.Scene.bEdgeSplit = bEdgeSplit 

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setGlossMix( bGlossMix ):
	bpy.types.Scene.bGlossMix = bpy.props.BoolProperty()
	bpy.types.Scene.bGlossMix = bGlossMix;

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setGloss( Glossfactor, GlossRough ):
	bpy.types.Scene.Glossfactor = bpy.props.FloatProperty()
	bpy.types.Scene.Glossfactor = Glossfactor
	bpy.types.Scene.GlossRough = bpy.props.FloatProperty()
	bpy.types.Scene.GlossRough = GlossRough

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setOutLocAndType( path, type ):
	renderSettings = bpy.context.scene.render
	renderSettings.filepath = path
	renderSettings.image_settings.file_format = type

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setHorizonColor( r, g, b, strength ):
	mcjAddSky.addHorizonColor( r, g, b, strength )
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setHorizonColorBlender( r, g, b, strength ):
	mcjAddSky.addHorizonColorBlender( r, g, b, strength )
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setEnvTex( image, strength ):
	mcjAddSky.addSky( image, strength )
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setEnvTexBlender( image, strength ):
	mcjAddSky.addSkyBlender( image, strength )

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setImageSize( width, height ):
	bpy.context.scene.render.resolution_percentage = 100
	bpy.context.scene.render.resolution_x = width
	bpy.context.scene.render.resolution_y = height

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def addLight( name, x, y, z, intensity, red, green, blue ):
	bpy.ops.object.lamp_add( type='POINT', view_align=False, location=(x, y, z), rotation=(0.0, 0.0, 0.0))
	lamp1 = bpy.context.object
	lamp1.name = name
	lamp1.data.shadow_method = 'RAY_SHADOW'
	lamp1.data.use_nodes = True
	tree = lamp1.data.node_tree
	nodes = tree.nodes
	for node in nodes:
		if node.type == "EMISSION":
			node.inputs[0].default_value = [red/255,green/255,blue/255,1]
			node.inputs[1].default_value = intensity*100*0.4

#-------------------------------------------------------------------------------		
# add camera , set its position, orientation and focal length
# make it the active camera, snap View3D to it
#-------------------------------------------------------------------------------		
def addCamera( x, y, z, rx, ry, rz, fl ):
	scene = bpy.context.scene
	nucamdata = bpy.data.cameras.new( 'nucam' )
	nucam = bpy.data.objects.new( 'nucam', nucamdata )
	scene.objects.link(nucam)
	#rotations rx, ry, rz are in degrees, XYZ rotation order
	nucamdata.lens = float( fl )
	nucam.location = ( float(x), float(y), float(z) )
	nucam.rotation_euler = ( rad(float(rx)), rad(float(ry)), rad(float(rz)) )
	nucamdata.clip_end = 1000
	scene.camera = nucam
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			area.spaces[0].region_3d.view_perspective = 'CAMERA'

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def getCommandLineFrame():
	argc = len( sys.argv )
	frame = 0;
	for i in range(argc):
		if( sys.argv[i] == "-f" ):
			if( i+1 < argc ):
				frame = int(sys.argv[i+1])
			break;
	return( frame )

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setRenderEngine( engine ):
	if( engine != "AS_IS" ):
		bpy.context.scene.render.engine = engine

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def setCyclesSettings( feature_set, device, gpu_type, samples ):
	if( bpy.context.scene.render.engine == "CYCLES" ):
		bpy.context.scene.cycles.feature_set = feature_set
		bpy.context.scene.cycles.device = device
		bpy.context.scene.cycles.gpu_type = gpu_type
		bpy.context.scene.cycles.samples = samples
			
#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def rad(a):
	return( a * 3.141593 / 180.0 )

#-------------------------------------------------------------------------------		
#
#-------------------------------------------------------------------------------		
def loadfix( objFile, postLoadProcessor, matLibPath, bGammaFix ):
	if( bpy.context.scene.render.engine == "CYCLES" ):
		bpy.context.scene.cycles.seed = random.randint(0,65535)
	#get rid of the default cube
	if "Cube" in bpy.data.objects:
		ob = bpy.data.objects["Cube"]
		bpy.context.scene.objects.unlink(ob)
		bpy.data.objects.remove(ob)
	if "Lamp" in bpy.data.objects:
		ob = bpy.data.objects["Lamp"]
		bpy.context.scene.objects.unlink(ob)
		bpy.data.objects.remove(ob)
	# build list of objects in the scene before the .obj load
	aObjectsBefore = []
	for obj in bpy.data.objects:
		aObjectsBefore.append( obj.name )
	# mark materials in the scene as untouchables
	# and rename them so they dont clash with materials that 
	# are about to be created ( and the names in the material library
	
	if( postLoadProcessor == "USEMATLIB" ):
		#rename mats in the scene to prevent clashes with material-libtrary
		mcjUseMatLib.hideMats();
	
	bpy.ops.object.select_all(action='DESELECT')
	
	#import .obj/.mtl
	gm = axis_conversion( from_forward='-Z', from_up='Y' ).to_4x4()
	bpy.ops.import_scene.obj( filepath=objFile )
	# io_scene_obj.import_obj.load(bpy.ops,bpy.context,objFile,global_matrix=gm)
	

	try:
		bSmooth = bpy.types.Scene.bSmooth
	except AttributeError:
		bSmooth = False
	try:
		bEdgeSplit = bpy.types.Scene.bEdgeSplit
	except AttributeError:
		bEdgeSplit = False
	split_angle = 80.0 * 3.1416 / 180.0
	for obj in bpy.data.objects:
		obj.select = False
	for obj in bpy.data.objects:
		if obj not in aObjectsBefore:
			if obj.type == 'MESH':
				obj.select = True
				bpy.context.scene.objects.active = obj
				if bSmooth: 
					bpy.ops.object.shade_smooth()
				if bEdgeSplit: 
					if not "EdgeSplit" in obj.modifiers:
						bpy.ops.object.modifier_add(type='EDGE_SPLIT')
						mod = obj.modifiers['EdgeSplit']
						mod.split_angle = split_angle
				obj.select = False
	if bGammaFix:
		mcjGammaFix.fixObjectsExcept( aObjectsBefore )
		
	# post load processing
	if( postLoadProcessor == "CYCLESMATS" ):
		mcjMakeCyclesNodes.fixObjectsExcept( aObjectsBefore )
		mcjAddMappersToTexImgs.addMappingToAllObjects()
	elif( postLoadProcessor == "BLENDERFIX" ):
		mcjFixBlenderMats.fixObjectsExcept( aObjectsBefore, bGammaFix )
	elif( postLoadProcessor == "USEMATLIB" ):
		mcjUseMatLib.switchToLibraryMaterials( matLibPath )
	else :
		print( "no post-load processing" );
	mcjMatsFromFilename.switchToNamedMaterials();
	
# ---------- createIRayMaps ----------
def createIRayMaps( shader, nodeName, parentName, nodeLabel, matName, metallicity, diffuse, diffColor, translucent, transColor, transWeight, specular, specColor, specWeight, specRefl, specRough, specAnisotropy, specRotation, refraction, refractWeight, refractIndex, bump, bumpSize, top, topColor, topWeight, topRefl, topRough, topAnisotropy, topRotation, SSScolor, SSSdistance, SSSamount, cutout, cutoutWeight, thinWall ):
	print( "Iray shaders for " + nodeName + ": " + matName )
	matBlenderName = matName.replace (" ", "_")
	obj = intelliFindObj( nodeName )
	mtrslt = 0
	if obj:
		mtrslt	= intelliFindMat( obj, nodeName, matBlenderName )
	else:
		print( "	Unable to find an object named " + nodeName + "; trying other objects." )
		if parentName:
			parentObj = intelliFindObj( parentName )
			longname = matBlenderName + "_" + nodeLabel
			longname = longname.replace( " ", "_" )
			mtrslt = intelliFindMat( parentObj, parentName, longname )
			if not mtrslt:
				mtrslt = intelliFindMat( parentObj, parentName, matBlenderName )
		
	if mtrslt:
		mat = mtrslt.material;
		tree = mat.node_tree
		nodes = tree.nodes
		nodes.clear()
		outNode = nodes.new( 'ShaderNodeOutputMaterial' )
		ox = outNode .location.x
		oy = outNode .location.y
		links = tree.links
		
		# Set up default shader
		bsdfNode = nodes.new( 'ShaderNodeGroup' )
		bsdfNode.node_tree = bpy.data.node_groups[shader]
		bsdfNode.location = ( ox - 600, oy )
		links.new( bsdfNode.outputs[0], outNode.inputs[0] )
		
		bsdfNode.inputs[0].default_value = metallicity
		if( diffuse ):
			diffNode = addImage( diffuse, ox - 1200, oy + 500, nodes )
			diffNode.label = "Base Color"
			
			links.new( diffNode.outputs[0], bsdfNode.inputs[2] )
		bsdfNode.inputs[1].default_value = diffColor
		
		if( translucent ):
			transNode = addImage( translucent, ox - 1200, oy +250, nodes )
			transNode.label = "Translucent Color"
			links.new( transNode.outputs[0], bsdfNode.inputs[6] )
		bsdfNode.inputs[4].default_value = transWeight
		bsdfNode.inputs[5].default_value = transColor
		if( specular ):
			specNode = addImage( specular, ox - 1200, oy, nodes )
			specNode.label = "Specular"
			specNode.color_space = 'NONE'
			links.new( specNode.outputs[0], bsdfNode.inputs[9] )
		bsdfNode.inputs[7].default_value = specWeight
		bsdfNode.inputs[8].default_value = specColor
		bsdfNode.inputs[10].default_value = specRough
		bsdfNode.inputs[11].default_value = specRefl
		bsdfNode.inputs[12].default_value = specAnisotropy
		bsdfNode.inputs[13].default_value = specRotation
		if( bump ):
			bumpNode = addImage( bump, ox - 1200, oy - 250, nodes )
			bumpNode.label = "Bump"
			bumpNode.color_space = 'NONE'
			links.new( bumpNode.outputs[0], bsdfNode.inputs[15] )
			links.new( bumpNode.outputs[0], bsdfNode.inputs[30] )
		bsdfNode.inputs[14].default_value = bumpSize
		if ( refraction ):
			refractNode = addImage( refraction, ox - 1500, oy - 375, nodes )
			refractNode.label = "Refraction"
			refractNode.color_space = 'NONE'
			links.new( refractNode.outputs[0], bsdfNode.inputs[17] )
		else:
			bsdfNode.inputs[17].default_value = refractWeight
		bsdfNode.inputs[18].default_value = refractIndex
		if( top ):
			topNode = addImage( top, ox - 1200, oy - 500, nodes )
			topNode.label = "Top Coat"
			topNode.color_space = 'NONE'
			links.new( topNode.outputs[0], bsdfNode.inputs[22] )
		bsdfNode.inputs[21].default_value = topWeight
		bsdfNode.inputs[23].default_value = topColor
		bsdfNode.inputs[24].default_value = topRough
		bsdfNode.inputs[25].default_value = topRefl
		bsdfNode.inputs[26].default_value = topAnisotropy
		bsdfNode.inputs[27].default_value = topRotation
		bsdfNode.inputs[29].default_value = bumpSize
		bsdfNode.inputs[32].default_value = SSScolor
		bsdfNode.inputs[33].default_value = SSSdistance
		bsdfNode.inputs[34].default_value = SSSamount
		if( cutout ):
			cutNode = addImage( cutout, ox - 1200, oy - 750, nodes )
			cutNode.label = "Cutout"
			cutNode.color_space = 'NONE'
			links.new( cutNode.outputs[0], bsdfNode.inputs[31] )
		else:
			bsdfNode.inputs[31].default_value = cutoutWeight
		bsdfNode.inputs[36].default_value = thinWall
	else:
		print ( "	Unable to find a material named " + matName )
	
def addImage( image, nx, ny, nodes ):
	imgNode = nodes.new( 'ShaderNodeTexImage' )
	imgNode.location = ( nx, ny )
	for img in bpy.data.images:
		if( img.filepath == image ):
			imgNode.image = img
			print( "	Found " + image + " and reused it" )
			return( imgNode )
	imgNode.image = bpy.data.images.load( image )
	print( "	Added " + image )
	if '/temp/' in image:
		imgNode.image.pack()
		print( "	Packed " + image + " into blend file" )
	return( imgNode )
