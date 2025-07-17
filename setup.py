from setuptools import setup, find_packages

setup(
    name='ddos-ziole',
    version='1.0.0',
    author='oozvc',
    author_email='oozvc.co@gmail.com',
    description='Advanced DDoS Toolkit by Ziole - for testing purposes only!',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/oozvc/ddos-ziole',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'colorama',
        'rich',
        'psutil',
        'pyfiglet'
        'requests websocket-client'
        # Tambahin modul lain yang dipake kalau ada
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD 3-Clause License',  # ganti kalo lo pake lisensi lain
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Development Status :: 4 - Beta',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'ddos-ziole=main:ddosv14'  # asumsi file utama bernama main.py dan punya def main()
        ]
    },
    keywords='ddos attack network stress testing ziole',
)
