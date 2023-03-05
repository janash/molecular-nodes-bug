import bpy

"""
This is in nodes and col modules in original MolecularNodes

Find a way to leverage this for individual selection as a backup solution

Affects GeometryNodes UI and will be done one selection to one frame 

NOTE: Boolean is_solvent Attribute  is registered to mol_sel_atom_prop in the panel UI of GeometryNodes

INSTEAD of immediate bond recalculation 

"""


# append the node properties to the aseset/blend file
def mol_append_node(node_name):
    if bpy.data.node_groups.get(node_name):
        pass
    else:
        before_data = list(bpy.data.node_groups)
        bpy.ops.wm.append(
            directory = os.path.join(
                    os.path.dirname(__file__), 'assets', 'node_append_file.blend' + r'/NodeTree'), 
                    filename = node_name, 
                    link = False
                )   
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.node_groups)))
    
    return bpy.data.node_groups[node_name]

def mol_base_material():
    """Append MOL_atomic_material to the .blend file it it doesn't already exist, and return that material."""
    mat = bpy.data.materials.get('MOL_atomic_material')
    
    if not mat:
        mat = bpy.ops.wm.append(
            directory=os.path.join(
                mn_folder, 'assets', 'node_append_file.blend' + r'/Material'
            ), 
            filename='MOL_atomic_material', 
            link=False
        )
    
    return mat


def add_custom_node_group(parent_group, node_name, location = [0,0], width = 200):
    
    mol_append_node(node_name)
    
    node = parent_group.node_group.nodes.new('GeometryNodeGroup')
    node.node_tree = bpy.data.node_groups[node_name]
    
    node.location = location
    node.width = 200 # unsure if width will work TODO check
    
    return node

def add_custom_node_group_to_node(parent_group, node_name, location = [0,0], width = 200):
    
    mol_append_node(node_name)
    
    node = parent_group.nodes.new('GeometryNodeGroup')
    node.node_tree = bpy.data.node_groups[node_name]
    
    node.location = location
    node.width = 200 # unsure if width will work TODO check
    
    return node



def mol_add_node(node_name):
    prev_context = bpy.context.area.type
    bpy.context.area.type = 'NODE_EDITOR'
    # actually invoke the operator to add a node to the current node tree
    # use_transform=True ensures it appears where the user's mouse is and is currently 
    # being moved so the user can place it where they wish
    bpy.ops.node.add_node(
        'INVOKE_DEFAULT', 
        type='GeometryNodeGroup', 
        use_transform=True
        )
    bpy.context.area.type = prev_context
    bpy.context.active_node.node_tree = bpy.data.node_groups[node_name]
    bpy.context.active_node.width = 200.0
    # if added node has a 'Material' input, set it to the default MN material
    input_mat = bpy.context.active_node.inputs.get('Material')
    if input_mat:
        input_mat = nodes.mol_base_material().name











#class to actually call the node group
class MOL_OT_Add_Custom_Node_Group(bpy.types.Operator):
    bl_idname = "mol.add_custom_node_group"
    bl_label = "Add Custom Node Group"
    # bl_description = "Add Molecular Nodes custom node group."
    bl_options = {"REGISTER", "UNDO"}
    node_name: bpy.props.StringProperty(
        name = 'node_name', 
        description = '', 
        default = '', 
        subtype = 'NONE', 
        maxlen = 0
    )
    node_description: bpy.props.StringProperty(
        name = "node_description", 
        description="", 
        default="Add MolecularNodes custom node group.", 
        subtype="NONE"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    @classmethod
    def description(cls, context, properties):
        return properties.node_description
    
    def execute(self, context):
        try:
            nodes.mol_append_node(self.node_name)
            mol_add_node(self.node_name)
        except RuntimeError:
            self.report({'ERROR'}, 
                        message='Failed to add node. Ensure you are not in edit mode.')
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)