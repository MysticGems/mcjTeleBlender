bl_info = {
    "name": "mcjTeleBlender",
    "version": (1, 0),
    "author": "mCasualJacques",
    "blender": (2, 72, 0),
    "description": "DAZ 3D to Blender conversion",
    "category": "DAZ 3D"}
import bpy
import os

#---------- findMat ----------
def findMat(name):
	if( name == "" ):
		return( 0 )
	for mat in bpy.data.materials:
		if( mat.name == name ):
			return( mat )
	return( 0 );


#---------- getMap ----------
def getMap( mat, key ):
	texSlots = mat.texture_slots;
	for t in texSlots:
		if hasattr( t,'texture' ):
			if hasattr( t.texture, 'image' ):
				if hasattr( t.texture.image, 'filepath' ):
					imgPath = t.texture.image.filepath;
					name = os.path.split(imgPath);
					if name[1].startswith( key ):
						prefix = name[1].split(".")[0]
						return( [name[0], prefix] )

	return 0
	
#---------------------------------------------
#	 
#---------------------------------------------
def getNamedLib( mat ):
	libmatname = getMap( mat, "lib_" );
	if( libmatname ):
		path = libmatname[0];
		name = libmatname[1];
		matLib = ( path + "/" + name + ".blend" );
		matNamesList = [];
		matNamesList.append( {'name': name } );
		if os.path.exists( matLib ):
			bpy.ops.wm.link_append( directory=matLib + "/Material/", link=False, files=matNamesList )
			return( findMat(name) );
		else:	
			print( "problem cant find named lib " + matLib )
			return( 0 );
	return( 0 );

#---------------------------------------------
#	 
#---------------------------------------------
def switchToNamedMaterials():
	for obj in bpy.data.objects:
		for mtrlslt in obj.material_slots:
			mat = mtrlslt.material;
			namedLibMat = getNamedLib( mat )
			if namedLibMat:
				mtrlslt.material = namedLibMat;
	