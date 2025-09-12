# Dashboard Structure

This directory contains the Streamlit dashboard for the referee scheduling system, organized as a multipage application.

## File Structure

```
dashboard/
├── main.py                        # Main entry point and navigation
├── app.py                         # DEPRECATED - redirects to main.py
├── pages/
│   ├── Availability_Setup.py     # Step 1: Upload and manage referee availability
│   └── Game_Management.py        # Step 2: Define games and run scheduling
└── utils/
    ├── __init__.py               # Package initialization
    ├── template_generator.py     # Excel template creation functions
    └── file_processor.py         # File upload and processing utilities
```

## How to Run

### Primary Method (Recommended)
```bash
cd dashboard
streamlit run main.py
```

### Legacy Method (Will redirect)
```bash
cd dashboard
streamlit run app.py  # Will show redirect page
```

## Page Organization

### Main Page (`main.py`)
- System overview and status
- Quick navigation to workflow steps
- Progress tracking

### Availability Setup (`pages/Availability_Setup.py`)
- Download availability templates (standard and custom)
- Upload completed availability files
- View and analyze current availability data
- Data validation and error handling

### Game Management (`pages/Game_Management.py`)
- Define number of games per time slot
- Run scheduling algorithms (Greedy implemented, Optimization planned)
- Review and edit generated schedules
- Export final schedules

## Utilities

### Template Generator (`utils/template_generator.py`)
- `create_template()`: Simple CSV template
- `create_custom_template()`: Customizable Excel template with checkboxes

### File Processor (`utils/file_processor.py`)
- `process_uploaded_file()`: Handle CSV/Excel uploads
- `convert_referee_format_to_matrix()`: Parse Excel checkbox format
- `load_availability_data()`: Load existing data
- `clear_availability_data()`: Reset data

## Features

### ✅ Implemented
- Multi-page navigation
- Excel template generation with checkboxes
- File upload and processing
- Availability data visualization
- Game definition interface
- Basic scheduling algorithm integration

### 🚧 Planned (Phase 2)
- Interactive schedule editor (drag & drop)
- Real-time conflict detection
- Advanced optimization algorithms
- Schedule analytics dashboard
- Automated email notifications
- Payroll integration

## Development Notes

- Each page is self-contained with its own imports
- Shared utilities are centralized in the `utils/` package
- Streamlit's multipage structure automatically creates sidebar navigation
- Page icons and names are embedded in filenames (Streamlit convention)

## Migration from Original app.py

The original monolithic `app.py` file has been broken down for better maintainability:

- **Navigation logic** → `main.py`
- **Template creation** → `utils/template_generator.py`
- **File processing** → `utils/file_processor.py`
- **Availability features** → `pages/Availability_Setup.py`
- **Game management** → `pages/Game_Management.py`

This structure makes it easier to:
- Add new pages and features
- Maintain and debug individual components
- Collaborate on different parts of the system
- Test individual modules
