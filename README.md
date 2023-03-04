# MolecularNodes Bug

First, we'll load in something that works. 
Then I will give you instructions on how to load in a system which makes the program crash.

I've included a topology and coordinate file for a simulation of a DNA helix with 10 bases.
You can load this in Blender using `MolecularNodes` md panel. 

**To use these test cases, use an unmodified version of MolecularNodes**

## Test Cases

### Case 1 - The Trajectory Loads Correctly
Make the following choices when importing:

* Choose "Ball and Stick" as the 
default representation.
* Delete the default selection.

You should see the molecular dynamics trajectory of a DNA molecule and some ions.

### Case 2 - The Trajectory Loads
Make the following choices when importing:

* Choose "Atoms"
* Leave the default selection.

### Case 3 - Blender Crashes
Make the following choices when imporing

* Choose "Ball and Stick" as the deault representation.
* Leave the default selection.

### Case 4 - The Trajectory Loads
Make the following choices when importing:

* Choose "Ball and Stick"
* Type `resid 21` in the defalt selection box.

You will see the trajectory of one single sodium ion.
`resid 21` means "residue ID 21". Our DNA has 10 base pairs, 
meaning that the first 20 residues are DNA. 

### Case 5 - Blender Crashes
Make the following choices when importing:

* Choose "Ball and Stick"
* Type `resid 20` in the defalt selection box.

`resid 20` represents the last DNA base pair.
It will be bonded to `resid 19`

### Conclusion: Partial selection of a molecule when using `Ball and Stick` makes Blender crash.

## Code Examination

To understand why we are seeing crashes, we have to isolate what is happening when a trajectory is loaded.

The relevant part of the `MolecularNodes` codes is in the `load_trajectory` function in `md.py`.

See the notebook selection.ipynb. It shows that when you select using MDAnalysis, references to atoms that are not
in the selection are left in the bond list.

## Solution - Discard bonds where the atom has been deleted.

From the above analysis, we can see that removing the bonds where an atom is not part of the selection might fix the crashing problem.
I chose to completely reorder the atoms and bonds, but that may not be necessary.
However, I based reordering on the `create_object` function.

```python
# create the initial model
mol_object = create_object(
    name = name,
    collection = coll.mn(),
    locations = univ.atoms.positions * world_scale, 
    bonds = bonds
)
```

You can see that the bonds are being passed having references to the atom indices. However, no atom indices are passed to
this function. Instead, just the locations of the atoms are passed. I thought it seemed safest to reorder (to test the need to reorder, one would need to add another test system where two molecules which are not sequential are loaded).

I wrote the following code to fix the problem, to replace the code around Line 110.

```python
if hasattr(univ, 'bonds') and include_bonds:

        # If there is a selection, we need to recalculate the bond indices
        if selection != "":
            index_map = { index:i for i, index in enumerate(univ.atoms.indices) }

            new_bonds = []
            for bond in univ.bonds.indices:
                try:
                    new_index = [index_map[y] for y in bond]
                    new_bonds.append(new_index)
                except KeyError:
                    # fragment - one of the atoms in the bonds was 
                    # deleted by the selection, so we shouldn't 
                    # pass this as a bond.  
                    pass
                
            bonds = np.array(new_bonds)
        else:
            bonds = univ.bonds.indices

    else:
        bonds = []
```

This code does two things 

- it reorders the bond indices
- it discards bonds where an atom is missing. This is done in the `try` statement and may be the most important part.

## Conclusion
After this change, you should be able to load all test cases specified in this document as well as Orion's test system with the default `MolecularNodes` selection.







