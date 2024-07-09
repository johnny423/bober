from bober.src.dtos import RFCSection


def rebuild_content(sections: list[RFCSection]) -> str:
    if not sections:
        return ""

    sorted_sections = sorted(sections, key=lambda s: s.row_start)

    result = []
    current_row = 1
    max_row = max(section.row_end for section in sorted_sections)

    for section in sorted_sections:
        # Fill in any gaps between sections
        result.extend([""] * (section.row_start - current_row))

        # Add the section content with proper indentation
        indent = "\t" * section.indentation
        result.extend(indent + line for line in section.content.splitlines())

        current_row = section.row_end + 1

    result.extend([""] * (max_row - current_row + 1))
    return "\n".join(result)
