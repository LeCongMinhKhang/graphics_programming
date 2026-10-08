from src.scene import Scene, AppOgl
import src.transform as transform
from src.shape_generators.three_dee import uv_sphere, torus
from src.shape_generators.tools import simple_ngonGenerator
from types import MethodType


def scenes(gl_app: AppOgl):
  someoneSmarterWouldHaveWrittenAClosedFormedFormula = [
    [ 2,],
    [ 2, 6,],
    [ 2, 6,10,],
    [ 2, 6,10,14],
    [ 2, 6,10,14,18],
    [ 2, 6,10,14,18,22],
    [ 2, 6,10,14,18,22,26],
  ]
  def aClosedFormedFormula(numE):
    tier = 0
    step = 0
    max   = lambda: tier >> 1
    limit = lambda: 2 + (max() - step) * 4
    layer = lambda: ((tier+1)>>1) + step
    res = [0 for i in range(7)]
    while numE > 0:
      if limit() < 0:
        step = 0
        tier += 1
      elif numE > limit():
        res[layer()] += limit()
        numE -= limit()
        step += 1
      elif numE <= limit():
        res[layer()] += numE
        numE -= limit()
    return res
      

  scenes = {}
  names = [
    "001-H-Hydrogen",
    "002-He-Helium",
    "003-Li-Lithium",
    "004-Be-Beryllium",
    "005-B-Boron",
    "006-C-Carbon",
    "007-N-Nitrogen",
    "008-O-Oxygen",
    "009-F-Fluorine",
    "010-Ne-Neon",
    "011-Na-Sodium",
    "012-Mg-Magnesium",
    "013-Al-Aluminium",
    "014-Si-Silicon",
    "015-P-Phosphorus",
    "016-S-Sulfur",
    "017-Cl-Chlorine",
    "018-Ar-Argon",
    "019-K-Potassium",
    "020-Ca-Calcium",
    "021-Sc-Scandium",
    "022-Ti-Titanium",
    "023-V-Vanadium",
    "024-Cr-Chromium",
    "025-Mn-Manganese",
    "026-Fe-Iron",
    "027-Co-Cobalt",
    "028-Ni-Nickel",
    "029-Cu-Copper",
    "030-Zn-Zinc",
    "031-Ga-Gallium",
    "032-Ge-Germanium",
    "033-As-Arsenic",
    "034-Se-Selenium",
    "035-Br-Bromine",
    "036-Kr-Krypton",
    "037-Rb-Rubidium",
    "038-Sr-Strontium",
    "039-Y-Yttrium",
    "040-Zr-Zirconium",
    "041-Nb-Niobium",
    "042-Mo-Molybdenum",
    "043-Tc-Technetium",
    "044-Ru-Ruthenium",
    "045-Rh-Rhodium",
    "046-Pd-Palladium",
    "047-Ag-Silver",
    "048-Cd-Cadmium",
    "049-In-Indium",
    "050-Sn-Tin",
    "051-Sb-Antimony",
    "052-Te-Tellurium",
    "053-I-Iodine",
    "054-Xe-Xenon",
    "055-Cs-Caesium",
    "056-Ba-Barium",
    "057-La-Lanthanum",
    "058-Ce-Cerium",
    "059-Pr-Praseodymium",
    "060-Nd-Neodymium",
    "061-Pm-Promethium",
    "062-Sm-Samarium",
    "063-Eu-Europium",
    "064-Gd-Gadolinium",
    "065-Tb-Terbium",
    "066-Dy-Dysprosium",
    "067-Ho-Holmium",
    "068-Er-Erbium",
    "069-Tm-Thulium",
    "070-Yb-Ytterbium",
    "071-Lu-Lutetium",
    "072-Hf-Hafnium",
    "073-Ta-Tantalum",
    "074-W-Tungsten",
    "075-Re-Rhenium",
    "076-Os-Osmium",
    "077-Ir-Iridium",
    "078-Pt-Platinum",
    "079-Au-Gold",
    "080-Hg-Mercury",
    "081-Tl-Thallium",
    "082-Pb-Lead",
    "083-Bi-Bismuth",
    "084-Po-Polonium",
    "085-At-Astatine",
    "086-Rn-Radon",
    "087-Fr-Francium",
    "088-Ra-Radium",
    "089-Ac-Actinium",
    "090-Th-Thorium",
    "091-Pa-Protactinium",
    "092-U-Uranium",
    "093-Np-Neptunium",
    "094-Pu-Plutonium",
    "095-Am-Americium",
    "096-Cm-Curium",
    "097-Bk-Berkelium",
    "098-Cf-Californium",
    "099-Es-Einsteinium",
    "100-Fm-Fermium",
    "101-Md-Mendelevium",
    "102-No-Nobelium",
    "103-Lr-Lawrencium",
    "104-Rf-Rutherfordium",
    "105-Db-Dubnium",
    "106-Sg-Seaborgium",
    "107-Bh-Bohrium",
    "108-Hs-Hassium",
    "109-Mt-Meitnerium",
    "110-Ds-Darmstadtium",
    "111-Rg-Roentgenium",
    "112-Cn-Copernicium",
    "113-Nh-Nihonium",
    "114-Fl-Flerovium",
    "115-Mc-Moscovium",
    "116-Lv-Livermorium",
    "117-Ts-Tennessine",
    "118-Og-Oganesson",
    ]
  
  def reserve_object(self, obj_name, func):
    entry = self.gl_app.objects.get(obj_name)
    obj_program_name = "interpolation"
    # if there is no more objects to reserve, create a new one
    if (entry is None) or (entry[0] >= len(entry[1])):
      obj = func()
      self.gl_app.create_program(obj_program_name)
      obj["program_id"] = self.gl_app.programs[obj_program_name]
      obj_id = self.gl_app.add_object(obj_name, obj)
      self.gl_app.objects[obj_name][0] += 1
    else:
      obj_program_name = self.gl_app.get_program_name(entry[1][entry[0] - 1])
      self.gl_app.objects[obj_name][0] += 1

    entry = self.gl_app.objects[obj_name]  # update the entry if object created
    obj_id = entry[1][entry[0] - 1]
    self.gl_app.objects_rendered.add(obj_id)
    return obj_id
  
  def make_build_scene(name):
    [electron,symbol,name] = name.split("-")
    electron = int(electron)
    def build_scene(self):
      self.program_name = "interpolation"
      self.gl_app.create_program("interpolation")
      configuration = aClosedFormedFormula(electron)
      # core
      obj = lambda: uv_sphere.generate(color = "hex", hex = 0xff0000)
      coreId = reserve_object(self,"atomCore",obj)
      self.update_object(
        coreId, 
        model_matrix=transform.identity(), 
        program_name="interpolation"
        )
      for i in range(len(configuration)):
        if configuration[i] == 0:
          continue
        # layer
        obj = lambda: torus.generate(thickness=0.1, hole_size=2*(1+i)-0.05, color = "hex", hex = 0xffffff)
        layerId = reserve_object(self,f"layer-{i}",obj)
        self.update_object(
          layerId,
          model_matrix=transform.identity(), 
          program_name="interpolation"
          )
        template = simple_ngonGenerator(configuration[i], 2*(1+i),0)
        for j in range(len(template)):
          # electron
          obj = lambda: uv_sphere.generate(n = 3, size=0.5, color = "hex", hex = 0x00fffff)
          electronId = reserve_object(self,f"electron-{i}-{j}",obj)
          self.update_object(
            electronId, 
            model_matrix=transform.translate(template[j][0],template[j][1],0), 
            program_name="interpolation"
            )
      
    return build_scene

  for name in names:
    scene = Scene(gl_app)
    scene.build_scene = MethodType(make_build_scene(name), scene)
    scenes[name] = scene

  return scenes