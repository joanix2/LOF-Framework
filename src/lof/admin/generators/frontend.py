"""Generates React/TypeScript frontend code from the intermediate schema."""

from lof.admin.schema.models import ApplicationSchema, ModelField, ModelSchema


def _ts_type(field: ModelField) -> str:
    mapping = {
        "string": "string",
        "text": "string",
        "integer": "number",
        "float": "number",
        "boolean": "boolean",
        "date": "string",
        "datetime": "string",
        "enum": "string",
        "uuid": "string",
    }
    return mapping.get(field.type, "string")


def generate_types(model: ModelSchema) -> str:
    lines = [f"export interface {model.name} {{"]
    for field in model.fields:
        if field.relation:
            continue
        ts_t = _ts_type(field)
        opt = "" if field.required else "?"
        if field.type == "enum":
            lines.append(f"  {field.name}{opt}: string;")
        else:
            lines.append(f"  {field.name}{opt}: {ts_t};")
    lines.append("}")
    lines.append("")

    lines.append(f"export interface {model.name}Create {{")
    for field in model.fields:
        if field.primary_key and field.generated:
            continue
        if field.relation:
            continue
        ts_t = _ts_type(field)
        opt = "" if field.required else "?"
        lines.append(f"  {field.name}{opt}: {ts_t};")
    lines.append("}")
    lines.append("")

    lines.append(f"export interface {model.name}Update {{")
    for field in model.fields:
        if field.primary_key and field.generated:
            continue
        if field.relation:
            continue
        lines.append(f"  {field.name}?: {_ts_type(field)};")
    lines.append("}")
    lines.append("")

    lines.append(f"export interface {model.name}ListParams {{")
    lines.append("  skip?: number;")
    lines.append("  limit?: number;")
    for field in model.fields:
        if field.ui.list.filterable:
            lines.append(f"  {field.name}?: string;")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def generate_service(model: ModelSchema) -> str:
    lines = [
        f"import api from '@/lib/api';",
        f"import {{{model.name}, {model.name}Create, {model.name}Update, {model.name}ListParams}} from './{model.name.lower()}.types';",
        "",
        f"export const {model.name.lower()}Service = {{",
        f"  list: (params?: {model.name}ListParams): Promise<{model.name}[]> =>",
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


def generate_hooks(model: ModelSchema) -> str:
    sn = model.name.lower()
    lines = [
        "import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';",
        f"import {{{model.name.lower()}Service}} from './{sn}.service';",
        f"import {{{model.name}, {model.name}Create, {model.name}Update}} from './{sn}.types';",
        "",
        f"export function use{model.name}s(params?: any) {{",
        f"  return useQuery({{",
        f"    queryKey: ['{sn}s', params],",
        f"    queryFn: () => {model.name.lower()}Service.list(params),",
        f"  }});",
        "}",
        "",
        f"export function use{model.name}(id: string) {{",
        f"  return useQuery({{",
        f"    queryKey: ['{sn}', id],",
        f"    queryFn: () => {model.name.lower()}Service.get(id),",
        f"    enabled: !!id,",
        f"  }});",
        "}",
        "",
        f"export function useCreate{model.name}() {{",
        "  const qc = useQueryClient();",
        f"  return useMutation({{",
        f"    mutationFn: (payload: {model.name}Create) => {model.name.lower()}Service.create(payload),",
        f"    onSuccess: () => qc.invalidateQueries({{ queryKey: ['{sn}s'] }}),",
        f"  }});",
        "}",
        "",
        f"export function useUpdate{model.name}() {{",
        "  const qc = useQueryClient();",
        f"  return useMutation({{",
        f"    mutationFn: ({{ id, payload }}: {{ id: string; payload: {model.name}Update }}) =>",
        f"      {model.name.lower()}Service.update(id, payload),",
        f"    onSuccess: () => qc.invalidateQueries({{ queryKey: ['{sn}s'] }}),",
        f"  }});",
        "}",
        "",
        f"export function useDelete{model.name}() {{",
        "  const qc = useQueryClient();",
        f"  return useMutation({{",
        f"    mutationFn: (id: string) => {model.name.lower()}Service.remove(id),",
        f"    onSuccess: () => qc.invalidateQueries({{ queryKey: ['{sn}s'] }}),",
        f"  }});",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_data_grid(model: ModelSchema) -> str:
    visible = [f for f in model.fields if f.ui.list.visible]
    columns = []
    for f in visible:
        if f.type == "enum":
            columns.append(f"      {{ key: '{f.name}', label: '{f.ui.label or f.name}', render: (v: string) => <Badge>{v}</Badge> }},")
        elif f.type == "boolean":
            columns.append(f"      {{ key: '{f.name}', label: '{f.ui.label or f.name}', render: (v: boolean) => v ? '✓' : '✗' }},")
        elif f.relation:
            columns.append(f"      {{ key: '{f.name}_id', label: '{f.ui.label or f.name}' }},")
        else:
            columns.append(f"      {{ key: '{f.name}', label: '{f.ui.label or f.name}' }},")

    sn = model.name.lower()
    lines = [
        "import { DataGrid, Column } from '@/components/DataGrid';",
        f"import {{{model.name}}} from './{sn}.types';",
        f"import {{ use{model.name}s, useDelete{model.name} }} from './{sn}.hooks';",
        "",
        f"const columns: Column<{model.name}>[] = [",
        *columns,
        "];",
        "",
        f"export function {model.name}DataGrid() {{",
        f"  const {{ data, isLoading }} = use{model.name}s();",
        f"  const deleteMutation = useDelete{model.name}();",
        "",
        "  return (",
        "    <DataGrid",
        f"      columns={{columns}}",
        "      data={{data || []}}",
        "      loading={{isLoading}}",
        "      onDelete={(row) => deleteMutation.mutate(row.id)}",
        "    />",
        "  );",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_form(model: ModelSchema) -> str:
    sn = model.name.lower()
    fields_jsx = []
    for field in model.fields:
        if field.primary_key and field.generated:
            continue
        label = field.ui.label or field.name
        required = field.required
        widget = field.resolved_widget()
        if widget == "textarea":
            fields_jsx.append(f'      <textarea {{...register("{field.name}", {{ required: {str(required).lower()} }})}} placeholder="{label}" />')
        elif widget in ("switch", "checkbox"):
            fields_jsx.append(f'      <label><input type="checkbox" {{...register("{field.name}")}} /> {label}</label>')
        elif widget == "select" and field.type == "enum":
            opts = "\n".join(f'        <option value="{v}">{v}</option>' for v in field.enum_values)
            fields_jsx.append(f'      <select {{...register("{field.name}", {{ required: {str(required).lower()} }})}}>')
            fields_jsx.append(f'        <option value="">-- {label} --</option>')
            for v in field.enum_values:
                fields_jsx.append(f'        <option value="{v}">{v}</option>')
            fields_jsx.append(f'      </select>')
        elif widget == "number-input":
            fields_jsx.append(f'      <input type="number" {{...register("{field.name}", {{ required: {str(required).lower()} }})}} placeholder="{label}" />')
        elif widget == "date-picker":
            fields_jsx.append(f'      <input type="date" {{...register("{field.name}", {{ required: {str(required).lower()} }})}} placeholder="{label}" />')
        elif widget == "datetime-picker":
            fields_jsx.append(f'      <input type="datetime-local" {{...register("{field.name}", {{ required: {str(required).lower()} }})}} placeholder="{label}" />')
        else:
            fields_jsx.append(f'      <input {{...register("{field.name}", {{ required: {str(required).lower()} }})}} placeholder="{label}" />')

    lines = [
        "import { useForm } from 'react-hook-form';",
        f"import {{{model.name}Create, {model.name}Update}} from './{sn}.types';",
        f"import {{ useCreate{model.name}, useUpdate{model.name} }} from './{sn}.hooks';",
        "",
        f"interface {model.name}FormProps {{",
        f"  id?: string;",
        f"  defaultValues?: Partial<{model.name}Create>;",
        f"  onSuccess?: () => void;",
        "}",
        "",
        f"export function {model.name}Form({{ id, defaultValues, onSuccess }}: {model.name}FormProps) {{",
        f"  const {{ register, handleSubmit }} = useForm({{ defaultValues }});",
        f"  const createMutation = useCreate{model.name}();",
        f"  const updateMutation = useUpdate{model.name}();",
        f"  const isEdit = !!id;",
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
        '    <form onSubmit={handleSubmit(onSubmit)}>',
        *fields_jsx,
        '      <button type="submit">{isEdit ? "Modifier" : "Créer"}</button>',
        "    </form>",
        "  );",
        "}",
        "",
    ]
    return "\n".join(lines)


def generate_list_page(model: ModelSchema) -> str:
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
        ("      <" + model.name + 'DataGrid onEdit={(id) => { setEditId(id); setOpen(true); }} />'),
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


def generate_all(app: ApplicationSchema) -> dict[str, str]:
    files: dict[str, str] = {}
    for model in app.models:
        prefix = f"apps/web/src/features/{model.name.lower()}"
        files[f"{prefix}/{model.name.lower()}.types.ts"] = generate_types(model)
        files[f"{prefix}/{model.name.lower()}.service.ts"] = generate_service(model)
        files[f"{prefix}/{model.name.lower()}.hooks.ts"] = generate_hooks(model)
        files[f"{prefix}/{model.name.lower()}_datagrid.tsx"] = generate_data_grid(model)
        files[f"{prefix}/{model.name.lower()}_form.tsx"] = generate_form(model)
        files[f"{prefix}/{model.name.lower()}_list_page.tsx"] = generate_list_page(model)
    return files
