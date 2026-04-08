import os
import io
import sys
import argparse
import subprocess

from entities import (
    VMF,
    QC,
    PropStatic
)

class DecompileError(Exception):
    ...

def decompile_model(modelPath: str, outFolder: str, crowbar: str):
    command = f'"{crowbar}" -p "{modelPath}" -o "{outFolder}"'
    result = subprocess.run(command, shell = True, capture_output = True, text = True)

    if result.returncode != 0:
        print(f"Failed to decompile {os.path.basename(modelPath)}.")
        raise DecompileError

class CompileError(Exception):
    ...

def compile_model(qcPath: str, studioMDL: str):
    command = f'"{studioMDL}" -nop4 "{qcPath}"'
    result = subprocess.run(command, shell = True, capture_output = True, text = True)

    if result.returncode != 0:
        print(f"Failed to compile {os.path.basename(qcPath)}.")
        raise CompileError

parser = argparse.ArgumentParser()

parser.add_argument("-vmf_in", required = True, help = ".vmf to use")
parser.add_argument("-vmf_out", required = True, help = "full filepath to output edited .vmf into")
parser.add_argument("-models_in", required = True, help = "content folder to pull models from (ie: 'custom' when folder structure is 'custom/models')")
parser.add_argument("-models_out", required = True, help = "folder to store decompiled models in (make this as short as possible)")
parser.add_argument("-bin", required = True, help = "bin folder for tools, ie: steamapps/common/GarrysMod/bin/win64")

def get_prop_statics(vmf: VMF) -> list[PropStatic]:
    prop_statics = []

    for instance in vmf.GetEntities():
        # Not our entity.
        if "prop_static" not in instance:
            continue

        try:
            rawValue = vmf.GetValueFromKey(instance, "uniformscale")
        except KeyError:
            continue

        uniformScale = float(rawValue)

        # Don't do work for prop_static instances that don't even need scaling.
        if uniformScale == 1.0:
            continue
        
        prop_statics.append(PropStatic(
            instance,
            int(vmf.GetValueFromKey(instance, "id")),
            vmf.GetValueFromKey(instance, "model"),
            uniformScale
        ))

    return prop_statics

def main():
    args = parser.parse_args()

    with io.open(args.vmf_in, "r", encoding = "utf8") as file:
        vmf = VMF(file.read(), args.vmf_in)

    crowbar = os.path.join(args.bin, "CrowbarCommandLineDecomp.exe")

    if not os.path.exists(crowbar):
        print(f"CrowbarCommandLineDecomp.exe not found in {args.bin}.\nExiting...")
        sys.exit(-1)

    studio_mdl = os.path.join(args.bin, "studiomdl.exe")

    if not os.path.exists(studio_mdl):
        print(f"studiomdl.exe not found in {args.bin}.\nExiting...")
        sys.exit(-1)

    prop_statics = get_prop_statics(vmf)
    decompiled = set()

    for prop in prop_statics:
        if prop.model in decompiled:
            continue

        model_path = os.path.join(args.models_in, os.path.normpath(prop.model))

        # This is safe, because it's guaranteed that the .mdl filetype is always there.
        qc_path = os.path.join(args.models_out, os.path.basename(prop.model.replace(".mdl", ".qc")))

        if os.path.exists(qc_path):
            continue

        print(f'Decompiling "{prop.model}"...')

        try:
            decompile_model(model_path, args.models_out, crowbar)
        except DecompileError:
            print(f"Scaling of '{prop.model}' failed, exiting...")
            sys.exit(-1)

        decompiled.add(prop.model)

    compiles: dict[str, set[float]] = {}

    for prop in prop_statics:
        # This is safe, because it's guaranteed that the .mdl filetype is always there.
        qc_path = os.path.join(args.models_out, os.path.basename(prop.model.replace(".mdl", ".qc")))

        # Don't compile a model that has already been scaled to the desired amount.
        if compiles.get(prop.model) and prop.uniformscale in compiles.get(prop.model):
            continue

        print(f'Compiling "{prop.model}" with {str(prop.uniformscale)} scale...')

        with io.open(qc_path, "r+", encoding = "utf8") as file:
            qc = QC(
                file.read(),
                qc_path
            )

            file.seek(0)

            try:
                # $scale doesn't affect $bbox, and $bbox is used to define boundaries which are used for model culling
                # so without this delete, models that are scaled up will disappear at certain angles.
                qc.DeleteKey("bbox")
            except KeyError:
                # cool, no bbox define
                pass

            model_define = prop.model[7:-4] + f"_scaled_{str(prop.uniformscale).replace(".", "_")}.mdl"
            qc.SetValue("modelname", '"' + model_define + '"')
            qc.SetValue("scale", str(prop.uniformscale))

            file.write(qc.string)
            file.truncate()

        compile_model(qc_path, studio_mdl)

        already_scaled = compiles.get(prop.model)

        if already_scaled is not None:
            already_scaled.add(prop.uniformscale)
        else:
            compiles[prop.model] = set([prop.uniformscale])

    print("Finished compiling models.\nScaled models were placed in your game's /models/ directory.")
    print(f"Editing '{os.path.basename(args.vmf_in)}'...")

    new_vmf = vmf.string

    for prop in prop_statics:
        new_instance = prop.instance.replace(".mdl", f"_scaled_{str(prop.uniformscale).replace(".", "_")}.mdl")
        new_instance = new_instance.replace(f'\n	"uniformscale" "{prop.uniformscale}"', "")

        # HACK: 'uniformscale' is sometimes stored as an integer without any decimal (ie: 2)
        if prop.uniformscale.is_integer():
            new_instance = new_instance.replace(f'\n	"uniformscale" "{int(prop.uniformscale)}"', "")

        new_vmf = new_vmf.replace(prop.instance, new_instance)

    with io.open(args.vmf_out, "w", encoding = "utf8") as file:
        file.write(new_vmf)

    print(f"Finished scaling '{os.path.basename(args.vmf_in)}'.\nExiting...")

if __name__ == "__main__":
    main()