"""Generates React/TypeScript frontend code from AdminModel adapter."""

from lof.admin.schema.adapter import AdminApp, AdminModel


def generate_types(model: AdminModel) -> str:
    lines = [f"export interface {model.name} {{"]
    for f in model.fields:
        if f.is_relation:
            continue
        opt = "" if f.required else "?"
        lines.append(f"  {f.name}{opt}: {f.ts_type};")
    lines.append("}")
    lines.append("")

    lines.append(f"export interface {model.name}Create {{")
    for f in model.fields:
        if f.name == "id":
            continue
        if f.is_relation:
            continue
        opt = "" if f.required else "?"
        lines.append(f"  {f.name}{opt}: {f.ts_type};")
    lines.append("}")
    lines.append("")

    lines.append(f"export interface {model.name}Update {{")
    for f in model.fields:
        if f.name == "id":
            continue
        if f.is_relation:
            continue
        lines.append(f"  {f.name}?: {f.ts_type};")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def generate_service(model: AdminModel) -> str:
    sn = model.name.lower()
    lines = [
        "import api from '@/lib/api';",
        f"import {{{model.name}, {model.name}Create, {model.name}Update}} from './{sn}.types';",
        "",
        f"export const {sn}Service = {{",
        f"  list: (params?: any): Promise<{model.name}[]> =>",
        f"    api.get('/{model.route_path}', {{ params }}).then(r => r.data),",
        f"  get: (id: string): Promise<{model.name}> =>",
        f"    api.get(`/{model.route_path}/${{id}}`).then(r => r.data),",
        f"  create: (payload: {model.name}Create): Promise<{model.name}> =>",
        f"    api.post('/{model.route_path}', payload).then(r => r.data),",
        f"  update: (id: string, payload: {model.name}Update): Promise<{model.name}> =>",
        f"    api.put(`/{model.route_path}/${{id}}`, payload).then(r => r.data),",
        f"  remove: (id: string): Promise<void> =>",
        f"    api.delete(`/{model.route_path}/${{id}}`),",
        "};",
        "",
    ]
    return "\n".join(lines)


def generate_hooks(model: AdminModel) -> str:
    sn = model.name.lower()
    lines = [
        "import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';",
        f"import {{{sn}Service}} from './{sn}.service';",
        f"import {{{model.name}, {model.name}Create, {model.name}Update}} from './{sn}.types';",
        "",
        f"export function use{model.name}s(params?: any) {{",
        "  return useQuery({",
        f"    queryKey: ['{sn}s', params],",
        f"    queryFn: () => {sn}Service.list(params),",
        "  });",
        "}",
        "",
        f"export function use{model.name}(id: string) {{",
        "  return useQuery({",
        f"    queryKey: ['{sn}', id],",
        f"    queryFn: () => {sn}Service.get(id),",
        "    enabled: !!id,",
        "  });",
        "}",
        "",
        f"export function useCreate{model.name}() {{",
        "  const qc = useQueryClient();",
        "  return useMutation({",
        f"    mutationFn: (payload: {model.name}Create) => {sn}Service.create(payload),",
        "    onSuccess: () => qc.invalidateQueries({ queryKey: ['{sn}s'] }),",
        "  });",
        "}",
        "",
        f"export function useUpdate{model.name}() {{",
        "  const qc = useQueryClient();",
        "  return useMutation({",
        f"    mutationFn: ({{ id, payload }}: {{ id: string; payload: {model.name}Update }}) =>",
        f"      {sn}Service.update(id, payload),",
        "    onSuccess: () => qc.invalidateQueries({ queryKey: ['{sn}s'] }),",
        "  });",
        "}",
        "",
        f"export function useDelete{model.name}() {{",
        "  const qc = useQueryClient();",
        "  return useMutation({",
        f"    mutationFn: (id: string) => {sn}Service.remove(id),",
        "    onSuccess: () => qc.invalidateQueries({ queryKey: ['{sn}s'] }),",
        "  });",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_data_grid(model: AdminModel) -> str:
    sn = model.name.lower()
    columns = []
    for f in model.fields_for_list():
        if f.type == "enum":
            columns.append(
                f"  {{ key: '{f.name}', label: '{f.name}', "
                f"render: (v: string) => <Badge>{{v}}</Badge> }},"
            )
        elif f.type == "boolean":
            columns.append(
                f"  {{ key: '{f.name}', label: '{f.name}', "
                f"render: (v: boolean) => v ? '\\u2713' : '\\u2717' }},"
            )
        else:
            columns.append(f"  {{ key: '{f.name}', label: '{f.name}' }},")

    col_str = "\n".join(columns)
    lines = [
        "import { DataGrid, Column } from '@/components/DataGrid';",
        f"import {{{model.name}}} from './{sn}.types';",
        f"import {{ use{model.name}s, useDelete{model.name} }} from './{sn}.hooks';",
        "",
        f"const columns: Column<{model.name}>[] = [",
        col_str,
        "];",
        "",
        f"export function {model.name}DataGrid() {{",
        f"  const {{ data, isLoading }} = use{model.name}s();",
        f"  const deleteMutation = useDelete{model.name}();",
        "",
        "  return (",
        "    <DataGrid",
        "      columns={columns}",
        "      data={data || []}",
        "      loading={isLoading}",
        "      onDelete={(row) => deleteMutation.mutate(row.id)}",
        "    />",
        "  );",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_form(model: AdminModel) -> str:
    sn = model.name.lower()
    fields_jsx = []
    for f in model.fields:
        if f.name == "id":
            continue
        label = f.name
        widget = f.widget
        if widget == "textarea":
            fields_jsx.append(
                f'      <textarea {{...register("{f.name}")}} placeholder="{label}" />'
            )
        elif widget in ("switch", "checkbox"):
            fields_jsx.append(
                f'      <label><input type="checkbox" {{...register("{f.name}")}} /> {label}</label>'
            )
        elif widget == "select" and f.enum_values:
            fields_jsx.append(
                f'      <select {{...register("{f.name}")}}>'
            )
            fields_jsx.append(f'        <option value="">-- {label} --</option>')
            for v in f.enum_values:
                fields_jsx.append(f'        <option value="{v}">{v}</option>')
            fields_jsx.append(f'      </select>')
        elif widget == "number-input":
            fields_jsx.append(
                f'      <input type="number" {{...register("{f.name}")}} placeholder="{label}" />'
            )
        elif widget in ("date-picker", "datetime-picker"):
            input_type = "datetime-local" if "datetime" in widget else "date"
            fields_jsx.append(
                f'      <input type="{input_type}" {{...register("{f.name}")}} '
                f'placeholder="{label}" />'
            )
        elif widget == "autocomplete":
            fields_jsx.append(
                f'      <input {{...register("{f.name}")}} placeholder="{label}" />'
            )
        else:
            fields_jsx.append(
                f'      <input {{...register("{f.name}")}} placeholder="{label}" />'
            )

    lines = [
        "import { useForm } from 'react-hook-form';",
        f"import {{{model.name}Create, {model.name}Update}} from './{sn}.types';",
        f"import {{ useCreate{model.name}, useUpdate{model.name} }} from './{sn}.hooks';",
        "",
        f"interface {model.name}FormProps {{",
        "  id?: string;",
        f"  defaultValues?: Partial<{model.name}Create>;",
        "  onSuccess?: () => void;",
        "}",
        "",
        f"export function {model.name}Form({{ id, defaultValues, onSuccess }}: {model.name}FormProps) {{",
        "  const { register, handleSubmit } = useForm({ defaultValues });",
        f"  const createMutation = useCreate{model.name}();",
        f"  const updateMutation = useUpdate{model.name}();",
        "  const isEdit = !!id;",
        "",
        "  const onSubmit = async (data: any) => {",
        "    try {",
        "      if (isEdit) {",
        f"        await updateMutation.mutateAsync({{ id, payload: data as {model.name}Update }});",
        "      } else {",
        f"        await createMutation.mutateAsync(data as {model.name}Create);",
        "      }",
        "      onSuccess?.();",
        "    } catch (e) {",
        "      console.error(e);",
        "    }",
        "  };",
        "",
        "  return (",
        "    <form onSubmit={handleSubmit(onSubmit)}>",
        *fields_jsx,
        '      <button type="submit">{isEdit ? "Modifier" : "Créer"}</button>',
        "    </form>",
        "  );",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_list_page(model: AdminModel) -> str:
    sn = model.name.lower()
    lines = [
        "import { useState } from 'react';",
        f"import {{{model.name}DataGrid}} from './{sn}_datagrid';",
        f"import {{{model.name}Form}} from './{sn}_form';",
        "",
        f"export function {model.name}ListPage() {{",
        "  const [open, setOpen] = useState(false);",
        "  const [editId, setEditId] = useState<string | undefined>();",
        "",
        "  return (",
        "    <div>",
        f"      <h1>{model.label_plural}</h1>",
        "      <button onClick={() => { setEditId(undefined); setOpen(true); }}>",
        f"        Nouveau {model.label}",
        "      </button>",
        "      <" + model.name + 'DataGrid onEdit={(id) => { setEditId(id); setOpen(true); }} />',
        "      {open && (",
        "        <div className='drawer'>",
        f"          <{model.name}Form",
        "            id={editId}",
        "            onSuccess={() => setOpen(false)}",
        "          />",
        "        </div>",
        "      )}",
        "    </div>",
        "  );",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_all(app: AdminApp) -> dict[str, str]:
    files = {}
    for model in app.models:
        prefix = f"apps/web/src/features/{model.name.lower()}"
        files[f"{prefix}/{model.name.lower()}.types.ts"] = generate_types(model)
        files[f"{prefix}/{model.name.lower()}.service.ts"] = generate_service(model)
        files[f"{prefix}/{model.name.lower()}.hooks.ts"] = generate_hooks(model)
        files[f"{prefix}/{model.name.lower()}_datagrid.tsx"] = generate_data_grid(model)
        files[f"{prefix}/{model.name.lower()}_form.tsx"] = generate_form(model)
        files[f"{prefix}/{model.name.lower()}_list_page.tsx"] = generate_list_page(model)
    return files
