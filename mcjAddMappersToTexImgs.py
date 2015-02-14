import bpy

bl_info = {
    "name": "mcjTeleBlender",
    "version": (1, 0),
    "author": "mCasualJacques",
    "blender": (2, 72, 0),
    "description": "DAZ 3D to Blender conversion",
    "category": "DAZ 3D"}

shaderLang = 0;

dictionary = [
	['ShaderNodeMapping', 'MAPPING'],
	['ShaderNodeTexImage', 'TEX_IMAGE'],
	['ShaderNodeTexCoord', 'TEX_COORD']
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
        

#---------- addMappingToMat ----------
def addMappingToMat( mat ):
	tree = mat.node_tree
	if not tree:
		mat.use_nodes = True
		tree = mat.node_tree
		if not tree:
			return
	nodes = tree.nodes
	links = tree.links
	for node in nodes:
		if( node.type in ['ShaderNodeTexImage','TEX_IMAGE'] ):
			#if node.type == 'ShaderNodeTexImage':
			#shaderLang = 0;
			#else:
			shaderLang = 1;
			if not socketOccupied( links, node.inputs[0] ):
				mappingNode = nodes.new(trad( 'ShaderNodeMapping'))
				mappingNode.location = ( node.location.x - 270, node.location.y )
				links.new( mappingNode.outputs['Vector'], node.inputs['Vector'] )
				texCoordNode = nodes.new(trad( 'ShaderNodeTexCoord'))
				texCoordNode.location = ( mappingNode.location.x - 270, mappingNode.location.y )
				links.new( texCoordNode.outputs['UV'], mappingNode.inputs['Vector'] )
        
#---------- addMappingToObject ----------
def addMappingToObject( o ):
	materials = o.material_slots
	for m in materials:
		mat = m.material
		if mat:
			addMappingToMat( mat )
    
#---------- addMappingToAllObjects ----------
def addMappingToAllObjects():
	objects = bpy.data.objects
	for o in objects:
		if o.type == 'MESH':
			addMappingToObject( o );	

