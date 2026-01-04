from setuptools import setup, find_packages

setup(
    name='biblioteko_backend',
    version='0.1.0',
    description='Backend pour CultureDiffusion',
    # Changed: We search packages starting from root (.), so 'src' becomes a package
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyramid',
        'waitress',
        'gitpython',
        'pyramid_chameleon',
        'pyramid_debugtoolbar',

        # Dépendances pour le convertisseur PDF
        'pdf2image',
        'pytesseract',
        'opencv-python',
        'Pillow',
        'numpy'
    ],
    entry_points={
        'paste.app_factory': [
            # Important: Point to the correct main function location
            # 'src.app' is the module, 'main' is the function
            'main = src.app:main',
        ],
    },
)