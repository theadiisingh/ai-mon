import sys
sys.path.insert(0, '.')

try:
    from app.main import app
    print('Import successful!')
    print(f'Routes registered: {len(app.routes)}')
    
    # List routes
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f'  {route.path}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    print('Test complete')

