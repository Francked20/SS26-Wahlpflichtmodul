import reflex as rx


class CompileException(Exception):
    pass


def title(text: str) -> rx.Component:
    return rx.vstack(
        rx.heading(
            text,
            weight="bold",
            size="8"
        ),
        rx.divider()
    )


def subtitle(text: str) -> rx.Component:
    return rx.vstack(
        rx.heading(
            text,
            weight="bold",
            size="6",
        ),
        rx.divider()
    )


def markdown(text: str) -> rx.Component:
    return rx.vstack(
        *[rx.markdown(line) for line in text.split(r"\n")],
        spacing="0",
    )


def code_block(
        text: str,
        language: str = "python",
        show_lines: bool = True,
        starting_line: int = 1,
) -> rx.Component:
    languages = rx.components.datadisplay.code.LiteralCodeLanguage.__args__
    lang = language.lower()

    if lang not in languages:
        raise CompileException(f"Language `{language}` not found!")

    return rx.scroll_area(
        rx.code_block(
            text,
            language=lang,  # type: ignore
            show_line_numbers=show_lines,
            starting_line_number=starting_line,
            theme="one-dark",
        ),
        scrollbars="horizontal",
        type="auto",
        class_name="widget-codeblock"
    )
