from typing import Any, cast

import libcst as cst

from lof.ast.adapter import AstAdapter
from lof.models.patch_definition import PatchOperation


class PythonLibCstAdapter(AstAdapter):
    def parse(self, source: str) -> cst.Module:
        return cst.parse_module(source)

    def unparse(self, tree: object) -> str:
        module = cast(cst.Module, tree)
        return module.code

    def apply_operation(
        self,
        tree: object,
        operation: PatchOperation,
        target_selector: dict[str, Any] | None = None,
    ) -> cst.Module:
        module = cast(cst.Module, tree)
        op = operation.op

        if op == "add_import":
            module = self._add_import(module, operation)
        elif op == "add_method":
            module = self._add_method(module, operation, target_selector)
        elif op == "add_decorator":
            module = self._add_decorator(module, operation, target_selector)
        elif op == "add_base_class":
            module = self._add_base_class(module, operation, target_selector)
        elif op == "replace_base_class":
            module = self._replace_base_class(module, operation, target_selector)
        elif op == "add_class_attribute":
            module = self._add_class_attribute(module, operation, target_selector)
        elif op == "replace_function_body":
            module = self._replace_function_body(module, operation)
        else:
            raise ValueError(f"Unknown operation: {op}")

        return cast(cst.Module, module)

    def _find_class(
        self, module: cst.Module, target_selector: dict[str, Any] | None
    ) -> cst.ClassDef | None:
        class_name = (target_selector or {}).get("class", "")
        for node in module.body:
            if isinstance(node, cst.ClassDef):
                if not class_name or node.name.value == class_name:
                    return node
        return None

    def _add_import(self, module: cst.Module, op: PatchOperation) -> cst.Module:
        module_name = op.module or ""
        import_name = op.import_name or ""
        alias = op.alias

        if module_name and import_name:
            attr = self._dotted_name(module_name)
            new_import = cst.ImportFrom(
                module=attr,
                names=[
                    cst.ImportAlias(
                        name=cst.Name(import_name),
                        asname=cst.AsName(name=cst.Name(alias)) if alias else None,
                    )
                ],
            )
        elif module_name and not import_name:
            new_import = cst.Import(
                names=[
                    cst.ImportAlias(
                        name=self._dotted_name(module_name),
                        asname=cst.AsName(name=cst.Name(alias)) if alias else None,
                    )
                ],
            )
        else:
            new_import = cst.Import(
                names=[cst.ImportAlias(name=cst.Name(import_name or module_name))],
            )

        new_body = list(module.body)
        new_body.insert(0, new_import)
        return module.with_changes(body=new_body)

    def _dotted_name(self, name: str) -> cst.Attribute | cst.Name:
        parts = name.split(".")
        if len(parts) == 1:
            return cst.Name(parts[0])
        attr = cst.Attribute(value=cst.Name(parts[0]), attr=cst.Name(parts[1]))
        for p in parts[2:]:
            attr = cst.Attribute(value=attr, attr=cst.Name(p))
        return attr

    def _add_method(
        self,
        module: cst.Module,
        op: PatchOperation,
        target_selector: dict[str, Any] | None = None,
    ) -> cst.Module:
        target_class = self._find_class(module, target_selector)
        if target_class is None:
            return module

        method_name = op.name or "new_method"
        params_list = op.parameters or []
        return_type = op.return_type
        body_lines = op.body or ["pass"]

        body_stmts = []
        for line in body_lines:
            try:
                stmt = cst.parse_statement(line.strip())
                body_stmts.append(stmt)
            except Exception:
                body_stmts.append(cst.parse_statement("pass"))

        param_elements = [cst.Param(name=cst.Name("self"))]
        for p in params_list:
            p_name = p.get("name", "arg")
            p_ann = p.get("annotation")
            annotation = cst.Annotation(cst.parse_expression(p_ann)) if p_ann else None
            param_elements.append(cst.Param(name=cst.Name(p_name), annotation=annotation))

        params = cst.Parameters(params=param_elements)
        returns = cst.Annotation(cst.parse_expression(return_type)) if return_type else None

        new_method = cst.FunctionDef(
            name=cst.Name(method_name),
            params=params,
            body=cst.IndentedBlock(body=body_stmts),
            returns=returns,
        )

        body_parts = list(target_class.body.body)
        body_parts.append(new_method)
        new_body = cst.IndentedBlock(body=body_parts)
        new_class = target_class.with_changes(body=new_body)

        new_body_list = [new_class if n is target_class else n for n in module.body]
        return module.with_changes(body=new_body_list)

    def _add_decorator(
        self,
        module: cst.Module,
        op: PatchOperation,
        target_selector: dict[str, Any] | None = None,
    ) -> cst.Module:
        target_class = self._find_class(module, target_selector)
        decorators = op.decorators or []
        if target_class is None:
            return module
        new_decorators = list(target_class.decorators)
        for dec in decorators:
            new_decorators.append(cst.Decorator(decorator=cst.Name(dec)))
        new_class = target_class.with_changes(decorators=new_decorators)
        new_body = [new_class if n is target_class else n for n in module.body]
        return module.with_changes(body=new_body)

    def _add_base_class(
        self,
        module: cst.Module,
        op: PatchOperation,
        target_selector: dict[str, Any] | None = None,
    ) -> cst.Module:
        target_class = self._find_class(module, target_selector)
        bases = op.bases or []
        if target_class is None:
            return module
        new_bases = list(target_class.bases)
        for b in bases:
            new_bases.append(cst.Arg(value=cst.Name(b)))
        new_class = target_class.with_changes(bases=new_bases)
        new_body = [new_class if n is target_class else n for n in module.body]
        return module.with_changes(body=new_body)

    def _replace_base_class(
        self,
        module: cst.Module,
        op: PatchOperation,
        target_selector: dict[str, Any] | None = None,
    ) -> cst.Module:
        target_class = self._find_class(module, target_selector)
        bases = op.bases or []
        if target_class is None:
            return module
        new_bases = [cst.Arg(value=cst.Name(b)) for b in bases]
        new_class = target_class.with_changes(bases=new_bases)
        new_body = [new_class if n is target_class else n for n in module.body]
        return module.with_changes(body=new_body)

    def _add_class_attribute(
        self,
        module: cst.Module,
        op: PatchOperation,
        target_selector: dict[str, Any] | None = None,
    ) -> cst.Module:
        target_class = self._find_class(module, target_selector)
        attributes = op.attributes or []
        if target_class is None:
            return module
        class_body = list(target_class.body.body)
        for attr in attributes:
            attr_name = attr.get("name", "new_attr")
            attr_ann = attr.get("annotation")
            attr_value = attr.get("value")
            ann = cst.Annotation(cst.parse_expression(attr_ann)) if attr_ann else None
            value = cst.parse_expression(attr_value) if attr_value else cst.Ellipsis()
            new_attr = cst.AnnAssign(
                target=cst.Name(attr_name),
                annotation=ann,
                value=value,
            )
            class_body.append(new_attr)
        new_indented = target_class.body.with_changes(body=class_body)
        new_class = target_class.with_changes(body=new_indented)
        new_body = [new_class if n is target_class else n for n in module.body]
        return module.with_changes(body=new_body)

    def _replace_function_body(self, module: cst.Module, op: PatchOperation) -> cst.Module:
        func_name = op.name or ""
        body_lines = op.body or ["pass"]
        body_stmts = []
        for line in body_lines:
            try:
                body_stmts.append(cst.parse_statement(line.strip()))
            except Exception:
                body_stmts.append(cst.parse_statement("pass"))

        new_body = []
        for node in module.body:
            if isinstance(node, cst.FunctionDef) and node.name.value == func_name:
                new_body.append(node.with_changes(body=cst.IndentedBlock(body=body_stmts)))
            else:
                new_body.append(node)
        return module.with_changes(body=new_body)
