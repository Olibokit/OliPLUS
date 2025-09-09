# 📦 manifest.py — Gestion cockpitifiée des types MIME pour fichiers Excel OpenXML

import os
from mimetypes import MimeTypes
from openpyxl.descriptors.serialisable import Serialisable
from openpyxl.descriptors import String, Sequence
from openpyxl.xml.functions import fromstring, tostring
from openpyxl.xml.constants import (
    ARC_CONTENT_TYPES, ARC_THEME, ARC_STYLE,
    THEME_TYPE, STYLES_TYPE, CONTYPES_NS,
    ACTIVEX, CTRL, VBA
)

# 🔧 Initialisation des MIME types cockpitifiés
mimetypes = MimeTypes()
custom_mimes = {
    ".xml": "application/xml",
    ".rels": "application/vnd.openxmlformats-package.relationships+xml",
    ".bin": "application/vnd.ms-office.vbaProject",
    ".vml": "application/vnd.openxmlformats-officedocument.vmlDrawing",
    ".emf": "image/x-emf"
}
for ext, mime in custom_mimes.items():
    mimetypes.add_type(mime, ext)

# 🧩 Structures typées
class FileExtension(Serialisable):
    tagname = "Default"
    Extension = String()
    ContentType = String()

    def __init__(self, Extension, ContentType):
        self.Extension = Extension
        self.ContentType = ContentType

class Override(Serialisable):
    tagname = "Override"
    PartName = String()
    ContentType = String()

    def __init__(self, PartName, ContentType):
        self.PartName = PartName
        self.ContentType = ContentType

# 📘 Définitions par défaut
DEFAULT_TYPES = [
    FileExtension("rels", custom_mimes[".rels"]),
    FileExtension("xml", custom_mimes[".xml"])
]

DEFAULT_OVERRIDE = [
    Override("/" + ARC_STYLE, STYLES_TYPE),
    Override("/" + ARC_THEME, THEME_TYPE),
    Override("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
    Override("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml")
]

# 🧠 Manifest cockpitifié
class Manifest(Serialisable):
    tagname = "Types"
    Default = Sequence(expected_type=FileExtension, unique=True)
    Override = Sequence(expected_type=Override, unique=True)
    path = "[Content_Types].xml"
    __elements__ = ("Default", "Override")

    def __init__(self, Default=None, Override=None):
        self.Default = Default or DEFAULT_TYPES
        self.Override = Override or DEFAULT_OVERRIDE

    @property
    def filenames(self):
        return [part.PartName for part in self.Override]

    @property
    def extensions(self):
        exts = {os.path.splitext(part.PartName)[-1] for part in self.Override}
        return [(ext[1:], mimetypes.types_map[True].get(ext)) for ext in sorted(exts) if ext]

    def to_tree(self):
        known_exts = {t.Extension for t in self.Default}
        for ext, mime in self.extensions:
            if ext not in known_exts and mime:
                self.Default.append(FileExtension(ext, mime))
        tree = super().to_tree()
        tree.set("xmlns", CONTYPES_NS)
        return tree

    def __contains__(self, content_type):
        return any(t.ContentType == content_type for t in self.Override)

    def find(self, content_type):
        return next(self.findall(content_type), None)

    def findall(self, content_type):
        return (t for t in self.Override if t.ContentType == content_type)

    def append(self, obj):
        self.Override.append(Override(obj.path, obj.mime_type))

    def _write(self, archive, workbook):
        self.append(workbook)
        self._write_vba(workbook)
        self._register_mimetypes(archive.namelist())
        archive.writestr(self.path, tostring(self.to_tree()))

    def _register_mimetypes(self, filenames):
        for fn in filenames:
            ext = os.path.splitext(fn)[-1]
            if ext:
                mime = mimetypes.types_map[True].get(ext)
                if mime:
                    self.Default.append(FileExtension(ext[1:], mime))

    def _write_vba(self, workbook):
        if workbook.vba_archive:
            node = fromstring(workbook.vba_archive.read(ARC_CONTENT_TYPES))
            mf = Manifest.from_tree(node)
            for override in mf.Override:
                if override.PartName in (ACTIVEX, CTRL, VBA) and override.PartName not in self.filenames:
                    self.Override.append(override)
