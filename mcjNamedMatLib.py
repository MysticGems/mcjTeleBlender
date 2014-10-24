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

#---------------------------------------------        
# begin Section - by mCasualJacques 
#---------------------------------------------      
#---------------------------------------------      
#     
#---------------------------------------------      
def findMat(name):
    if( name == "" ):
        return( 0 )
    for mat in bpy.data.materials:
        if( mat.name == name ):
            return( mat )
    return( 0 );

#---------------------------------------------      
#     
#---------------------------------------------      
def hideMats():
    aMats = []
    n = len( bpy.data.materials )
    for i in range( 0, n ):
        aMats.append( bpy.data.materials[i] )
    for i in range( 0, n ):
        mat = aMats[i] 
        mat.name = "mcjhide%d"%i 
      
#---------------------------------------------      
#     
#---------------------------------------------      
def switchToLibraryMaterials( matLib ):
    # note: we are not using the exclusion list aObjectsBefore
    # instead we use the fact that pre-obj-load materials 
    # have been renamed to "mcjhide_____"
    
    # we add a string-property to the Material class
    # we'll use it to store the old name of the material
    bpy.types.Material.oldname = bpy.props.StringProperty()

    # store the name of each material in the Material.oldname
    # and rename them using a name not in the material library
    # as we rename materials, 
    # the bpy.data.materials list is being re-sorted
    # it's a case of constant moving targets
    # so we proceed with caution
    aMats = []
    n = len( bpy.data.materials )
    for i in range( 0, n ):
        aMats.append( bpy.data.materials[i] )
    for i in range( 0, n ):
        mat = aMats[i] 
        mat.oldname = mat.name
        mat.name = "mcjmat%d"%i

    #based of the oldnames, load the materials from the material library
    matNamesList = []
    for mat in bpy.data.materials:
        if( not mat.name.startswith( "mcjhide" ) ):
            matNamesList.append( {'name': mat.oldname} )
    bpy.ops.wm.link_append( directory=matLib + "/Material/", link=False, files=matNamesList )

    #based on the oldnames, switch to the newly loaded materials
    for obj in bpy.data.objects:
        for mtrlslt in obj.material_slots:
            numat = findMat( mtrlslt.material.oldname ) 
            if( numat ):
                mtrlslt.material = numat

