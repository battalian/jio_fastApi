import io
import zipfile
import os

from starlette.responses import StreamingResponse


def zip_files(filenames):
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
        for fpath in filenames:
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join('zip_folder', fname)
            # Add file, at correct path
            temp_zip.write(fpath, arcname=zip_path)
    return StreamingResponse(
        iter([zip_io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=config.zip"}
    )
