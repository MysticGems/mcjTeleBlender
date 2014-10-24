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
import mcjBlendBot

aObjectsBefore = []
split_angle = 80.0 * 3.1416 / 180.0
for obj in bpy.data.objects:
    obj.select = False
for obj in bpy.data.objects:
    if obj not in aObjectsBefore:
        if obj.type == 'MESH':
            obj.select = True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.shade_smooth()
            if not "EdgeSplit" in obj.modifiers:
                bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                mod = obj.modifiers['EdgeSplit']
                mod.split_angle = split_angle
            obj.select = False
mcjGammaFix.fixObjectsExcept( aObjectsBefore )
mcjMakeCyclesNodes.fixObjectsExcept( aObjectsBefore )
mcjAddMappersToTexImgs.addMappingToAllObjects()
mcjMatsFromFilename.switchToNamedMaterials();
mcjBlendBot.addCamera( 0.607, -2.74, 1.577, 83.465, 0, 32.987, 30.759 )


