"""
node md

"""


# check if a particular property already exists or not
def property_exists(prop_path, glob, loc):
    try:
        eval(prop_path, glob, loc)
        return True
    except:
        return False

socket_types = {
        'BOOLEAN'  : 'NodeSocketBool', 
        'GEOMETRY' : 'NodeSocketGeometry', 
        'INT'      : 'NodeSocketInt', 
        'MATERIAL' : 'NodeSocketMaterial', 
        'VECTOR'   : 'NodeSocketVector', 
        'STRING'   : 'NodeSocketString', 
        'VALUE'    : 'NodeSocketFloat', 
        'COLLETION': 'NodeSocketCollection', 
        'TEXTURE'  : 'NodeSocketTexture', 
        'COLOR'    : 'NodeSocketColor', 
        'IMAGE'    : 'NodeSocketImage'
    }

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

def gn_new_group_empty(name = "Geometry Nodes"):
    group = bpy.data.node_groups.get(name)
    # if the group already exists, return it and don't create a new one
    if group:
        return group
    
    # create a new group for this particular name and do some initial setup
    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    group.inputs.new('NodeSocketGeometry', "Geometry")
    group.outputs.new('NodeSocketGeometry', "Geometry")
    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.is_active_output = True
    input_node.select = False
    output_node.select = False
    input_node.location.x = -200 - input_node.width
    output_node.location.x = 200
    group.links.new(output_node.inputs[0], input_node.outputs[0])
    return group

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



"""
md mod

"""
    # returns a numpy array of booleans for each atom, whether or not they are in that selection
    def bool_selection(selection):
        return np.isin(univ.atoms.ix, univ.select_atoms(selection).ix).astype(bool)

    
    def att_atom_type():
        return np.array(univ.atoms.types, dtype = int)


    attributes = (
        {'name': 'atomic_number',   'value': att_atomic_number,   'type': 'INT',     'domain': 'POINT'}, 
        {'name': 'vdw_radii',       'value': att_vdw_radii,       'type': 'FLOAT',   'domain': 'POINT'},
        {'name': 'res_id',          'value': att_res_id,          'type': 'INT',     'domain': 'POINT'}, 
        {'name': 'res_name',        'value': att_res_name,        'type': 'INT',     'domain': 'POINT'}, 
        {'name': 'b_factor',        'value': att_b_factor,        'type': 'float',   'domain': 'POINT'}, 
        {'name': 'chain_id',        'value': att_chain_id,        'type': 'INT',     'domain': 'POINT'}, 
        {'name': 'atom_types',      'value': att_atom_type,       'type': 'INT',     'domain': 'POINT'}, 
        {'name': 'is_backbone',     'value': att_is_backbone,     'type': 'BOOLEAN', 'domain': 'POINT'}, 
        {'name': 'is_alpha_carbon', 'value': att_is_alpha_carbon, 'type': 'BOOLEAN', 'domain': 'POINT'}, 
        {'name': 'is_solvent',      'value': att_is_solvent,      'type': 'BOOLEAN', 'domain': 'POINT'}, 
        {'name': 'is_nucleic',      'value': att_is_nucleic,      'type': 'BOOLEAN', 'domain': 'POINT'}, 
        {'name': 'is_peptide',      'value': att_is_peptide,      'type': 'BOOLEAN', 'domain': 'POINT'}, 
    )
    
    for att in attributes:
        # tries to add the attribute to the mesh by calling the 'value' function which returns
        # the required values do be added to the domain.
        try:
            add_attribute(mol_object, att['name'], att['value'](), att['type'], att['domain'])
        except:
            warnings.warn(f"Unable to add attribute: {att['name']}.")




"""

ui mod
"""



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


def menu_item_interface(layout_function, 
                        label, 
                        node_name, 
                        node_description='Add custom MolecularNodes node group.'):
    op=layout_function.operator('mol.add_custom_node_group', 
                                text = label, emboss = True, depress=False)
    op.node_name = node_name
    op.node_description = node_description



class MOL_MT_Add_Node_Menu_Properties(bpy.types.Menu):
    bl_idname = 'MOL_MT_ADD_NODE_MENU_PROPERTIES'
    bl_label = ''
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        # currently nothing for this menu in the panel



class MOL_MT_Add_Node_Menu_Selections(bpy.types.Menu):
    bl_idname = 'MOL_MT_ADD_NODE_MENU_SELECTIONS'
    bl_label = ''
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        menu_item_interface(layout, 'Select Atoms', 'MOL_sel_atoms', 
                            "Separate atoms based on a selection field.\n" +
                            "Takes atoms and splits them into the selected atoms the \
                            inverted atoms, based on a selection field")
        menu_item_interface(layout, 'Separate Polymers', 'MOL_sel_sep_polymers', 
                            "Separate the Geometry into the different polymers.\n" + 
                            "Outputs for protein, nucleic & sugars")
        layout.separator()
        menu_chain_selection_custom(layout)
        menu_ligand_selection_custom(layout)
        layout.separator()
        menu_item_interface(layout, 'Atom Properties', 'MOL_sel_atom_propeties', 
                            "Create a selection based on the properties of the atom.\n\
                            Fields for is_alpha_carbon, is_backbone, is_peptide, \
                            is_nucleic, is_solvent and is_carb")
        menu_item_interface(layout, 'Atomic Number', 'MOL_sel_atomic_number', 
                            "Create a selection if input value equal to the \
                            atomic_number field.")
        menu_item_interface(layout, 'Element Name', 'MOL_sel_element_name', 
                            "Create a selection of particular elements by name. Only \
                            first 20 elements supported")
        layout.separator()
        menu_item_interface(layout, 'Distance', 'MOL_sel_distance', 
                            "Create a selection based on the distance to a selected \
                            object.\n The cutoff is scaled based on the objects scale \
                            and the 'Scale Cutoff' value.")
        menu_item_interface(layout, 'Slice', 'MOL_sel_slice', 
                            "Create a selection that is a slice along one of the XYZ \
                            axes, based on the position of an object.")
        layout.separator()
        menu_residues_selection_custom(layout)                        
        menu_item_interface(layout, 'Res ID Single', 'MOL_sel_res_id', 
                            "Create a selection if res_id matches input field")
        menu_item_interface(layout, 'Res ID Range', 'MOL_sel_res_id_range', 
                            "Create a selection if the res_id is within the given \
                            thresholds")
        menu_item_interface(layout, 'Res Name Peptide', 'MOL_sel_res_name', 
                            "Create a selection of particular amino acids by name")
        menu_item_interface(layout, 'Res Name Nucleic', 'MOL_sel_res_name_nucleic', 
                            "Create a selection of particular nucleic acids by name")
        menu_item_interface(layout, 'Res Whole', 'MOL_sel_res_whole', 
                            "Expand the selection to every atom in a residue, if any \
                            of those atoms are in the initial selection")
        menu_item_interface(layout, 'Res Atoms', 'MOL_sel_res_atoms', 
                            "Create a selection based on the atoms of a residue.\n" +
                            "Selections for CA, backbone atoms (N, C, O), sidechain \
                            and backbone")