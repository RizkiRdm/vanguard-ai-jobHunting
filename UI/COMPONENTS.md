// Ref: BLUEPRIN.md & ux_doc.md
# UI Components Documentation

Audit of standardized components in `UI/src/components`.

## Standard Patterns
- **Styling**: Tailwind CSS v4 utility classes. Use CSS variables from `index.css` (e.g., `--color-primary`).
- **Icons**: SVG imports from `UI/src/icons/`.
- **Typing**: React TypeScript interfaces.

## Component Library
| Component | Status | Location | Notes |
| :--- | :--- | :--- | :--- |
| `Button` | Standardized | `UI/src/components/ui/button/` | Variants: primary, outline. Sizes: sm, md. |
| `ComponentCard` | Standardized | `UI/src/components/common/` | Main container for UI elements. |
| `Alert` | Standardized | `UI/src/components/ui/alert/` | variants: success, error, warning, info. |
| `InputField` | Standardized | `UI/src/components/form/input/` | Needs verification on focus-ring. |

## Todo
- [ ] Migrate legacy hardcoded colors to CSS variables.
- [ ] Ensure all input components follow `InputField` focus-ring pattern.
