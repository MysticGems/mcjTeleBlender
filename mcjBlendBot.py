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

#-------------------------------------------------------------------------------		
# when daz studio finds a name that already exists in the mtl file
# it appends the node label (which sometimes differs from the node name
# default ----> default_mcjA3BodyconR_(2)
#-------------------------------------------------------------------------------	
def intelliFindMat( obj, nodeName, matName ):
	if matName in obj.material_slots:
		return( obj.material_slots[matName] )
	longname = matName + "_" + nodeName
	if longname in obj.material_slots:
		return( obj.material_slots[longname] )
	for slt in obj.material_slots:
		if slt.name.startswith( matName ):
			return( slt )
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
		mtrslt  = intelliFindMat( obj, nodeName, matName )
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
	io_scene_obj.import_obj.load(bpy.ops,bpy.context,objFile,global_matrix=gm)

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
def createIRayMaps( nodeName, parentName, nodeLabel, matName, diffuse, translucent, specular, bump ):
	print( "Iray shaders for " + nodeName + ": " + matName )
	matBlenderName = matName.replace (" ", "_")
	obj = intelliFindObj( nodeName )
	mtrslt = 0
	if obj:
		mtrslt  = intelliFindMat( obj, nodeName, matBlenderName )
	else:
		print( "  Unable to find an object named " + nodeName + "; trying other objects." )
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

		diffNode = nodes.new( 'ShaderNodeTexImage' )
		diffNode.location = ( ox - 1200, oy + 250 )
		diffImage = bpy.data.images.load( diffuse )
		if 'temp' in diffuse:
			diffImage.pack()
			print( "  Packed " + diffuse + " in blend file" )
		diffNode.image = diffImage
		diffNode.label = "Base Color"
		
		# Set up default shader
		bsdfNode = nodes.new( 'ShaderNodeGroup' )
		bsdfNode.node_tree = bpy.data.node_groups['Skin Shader']
		bsdfNode.location = ( ox - 600, oy )
		links.new( diffNode.outputs[0], bsdfNode.inputs[0] )
		links.new( bsdfNode.outputs[0], outNode.inputs[0] )
		
		if( translucent ):
			transNode = nodes.new( 'ShaderNodeTexImage' )
			transNode.location = ( ox - 1200, oy )
			transNode.image = bpy.data.images.load( translucent )
			if 'temp' in translucent:
				transNode.image.pack()
				print( "  Packed " + translucent + " in blend file" )
			transNode.label = "Translucent Color"
			links.new( transNode.outputs[0], bsdfNode.inputs[1] )
		if( specular ):
			specNode = nodes.new( 'ShaderNodeTexImage' )
			specNode.location = ( ox - 1200, oy - 250 )
			specNode.image = bpy.data.images.load( specular )
			if 'temp' in specular:
				specNode.image.pack()
				print( "  Packed " + specular + " in blend file" )
			specNode.label = "Specular"
			links.new( specNode.outputs[0], bsdfNode.inputs[2] )
		if( bump ):
			bumpNode = nodes.new( 'ShaderNodeTexImage' )
			bumpNode.location = ( ox - 1200, oy - 500 )
			bumpNode.image = bpy.data.images.load( bump )
			if 'temp' in bump:
				bumpNode.image.pack()
				print( "  Packed " + bump + " in blend file" )
			bumpNode.label = "Bump"
			links.new( bumpNode.outputs[0], bsdfNode.inputs[3] )
	else:
		print ( "  Unable to find a material named " + matName )
	
