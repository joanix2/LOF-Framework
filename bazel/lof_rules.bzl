"""Bazel rules for Language-Oriented Framework compilation."""

def _lof_compile_impl(ctx):
    types = ctx.files.types
    instances = ctx.files.instances
    templates = ctx.files.templates
    patches = ctx.files.patches
    schemas = ctx.files.schemas
    targets = ctx.files.targets

    output_dir = ctx.actions.declare_directory(ctx.label.name + "_out")

    inputs = []
    inputs.extend(types)
    inputs.extend(instances)
    inputs.extend(templates)
    inputs.extend(patches)
    inputs.extend(schemas)
    inputs.extend(targets)
    inputs.extend(ctx.files._lof_cli_data)

    ctx.actions.run(
        inputs = inputs,
        outputs = [output_dir],
        executable = ctx.executable._compiler,
        arguments = [
            "--output",
            output_dir.path,
            "--types-dir",
            "definitions/types",
            "--instances-dir",
            "instances",
            "--patches-dir",
            "patches",
            "--templates-dir",
            "templates",
            "--targets-dir",
            "definitions/targets",
        ],
        mnemonic = "LofCompile",
        progress_message = "Compiling LOF project",
        env = {
            "LOF_ROOT": ctx.label.package,
        },
    )

    return [DefaultInfo(files = depset([output_dir]))]

lof_compile = rule(
    implementation = _lof_compile_impl,
    attrs = {
        "types": attr.label_list(allow_files = [".json"], doc = "Type definition files"),
        "instances": attr.label_list(allow_files = [".json"], doc = "Instance files"),
        "templates": attr.label_list(allow_files = True, doc = "Template files"),
        "patches": attr.label_list(allow_files = [".json"], doc = "Patch files"),
        "schemas": attr.label_list(allow_files = [".json"], doc = "Schema files"),
        "targets": attr.label_list(allow_files = [".json"], doc = "Target definition files"),
        "_compiler": attr.label(
            default = Label("//tools:compile"),
            executable = True,
            cfg = "exec",
        ),
        "_lof_cli_data": attr.label(
            default = Label("//:lof_cli"),
            allow_files = True,
        ),
    },
)
