# FileJacket

FileJacket is a Python package initially created to handle files, and files from remote resources (downloads), for use in 
a personal project that automatically crawl and download multimedia content. It evolved from a simple structure 
paradigm to an orient-object one, as a mean to show some colleagues the advantages in maintainability this paradigm 
brings. 

As time went by, I thought that this 
component of my project could be a standalone package that I could share.

### So what is this project for and why to use it?

The main motivation for the existence of this package, initially, was my need to have a download system able to save 
and load files from multiple filesystems and run distinct pos-processors in it - parsing and generating hashes and 
HTTP's metadata are a few examples. 

This project obviously isn't that system. It is a bit of it, the part that I thought would make more sense as an 
independent package, able to load files and do other stuff related to file management and being easily extendable. You 
can extend the `FileSystem` class to make your local or remote filesystem compatible, you can extend the pipeline 
for data extraction, for generating hashes and many other useful things related to handling files.

To handler files this project provides the classes `File`, `StreamFile` and `ContentFile`. What distinguish one from 
another is the previously set pipeline for data extraction. Those class inherent from `BaseFile` that requires a 
pipeline but not implement one. 

Basically this project abstracted the loading and creation of files to avoid some encountered problems:

- When saving overwrite a file, and you are not aware of it;
- There exists a CHECKSUM related to the file that you are not aware, and should be associated with it;
- Updating CHECKSUM after file`s content is changed;
- Loading and saving in a remote filesystem is complicated and each filesystem have distinct api calls.

Thus, this project was created with focus in extendability and hopeful it will be useful for those that want to avoid the problems mentioned. 

### What resources this project offer when handling files?

The `BaseFile`, where all file`s class are inherent from in this project, allow for:

- Manually or automatically creating hashes for the content of file when saving;
- Searching and loading of hash for file in `CHECKSUM.<hash extension>` or `*.<hash extension>`;
- Checking the integrity of file with its hash;  
- Generating thumbnail for the file. Currently support epub, images (gif, jgp, png, tiff, ...), videos (mkv, mpeg, mp4, avi,...), psd, pdf and a few others;
- Generating a preview animated image for the content of file;
- Protect the original file if changes are made in the content (or not, if the option to override and not save a backup are disabled when saving);
- Renaming duplicated files on save if override is not allowed with filename in POSIX or Windows format (`<name> (1).<extension>` or `<name> - 1.<extension>`);
- Comparing two files following a pipeline to check if some attributes are equal (the pipeline is customizable with processors to check if name, size or whole content is the same);
- Serialize the file object to a generic JSON, a specific JSON (less size used than generic one) and Pickle; 
- Manually or automatically cache content when reading it. The content will automatically be cached in file or in memory if the stream source of file is not seekable (generally from an external source, e.g download);
- All the above to work with distinct FileSystem, be it local or from cloud providers (for it to work the FileSystemEngine class must be extended for the new filesystem, currently only Windows and Linux are implemented).

## How to use

Below I list some examples of how you could use this project.

### Loading a file

```python
from filejacket import File

# Load a file from local filesystem
my_file = File(path='<string: path to my file>')

# Load a file from remote or custom filesystem requires that the 
# class `FileSystem` be extend and passed through `file_system_handler` parameter.
my_file = File(
    path='<string: path to my file>', 
    file_system_handler='<class inherent from FileSystem: my_custom_filesystem>'
)

```

### Creating a new file

```python
from filejacket import ContentFile

# Create a new file manually without extracting data from any source.
my_file = ContentFile(run_extract_pipeline=False)
my_file.content = '<string or bytes: My content here>'
my_file.complete_filename_as_tuple = (
    '<string: filename>',
    '<string: extension without dot (.)>'
)
my_file.save_to = '<string: directory path where it will be saved>'
my_file.save()
```

```python
from filejacket import StreamFile

# Create a new file from a stream. 
my_file = StreamFile(metadata='<dict: my stream metadata>') # metadata is required by the 
# pipeline of data extraction, it can be empty if there is none. You can also avoid providing 
# metadata parameter if your custom extractor don`t require it. 
my_file.content = '<instance class inherent from BaseIO>'
my_file.save_to = '<string: directory path where it will be saved>'
my_file.save()

# Create a new file from a stream using a custom pipeline for data extraction:
my_file = StreamFile(extract_data_pipeline='<instance of Pipeline class: my custom pipeline') 
my_file.content = '<instance class inherent from BaseIO>'
my_file.save_to = '<string: directory path where it will be saved>'
my_file.save()
```

Any class inherent from `BaseFile` that not overwrite the property `content` (`ContentFile`, `StreamFile` and `File`), 
accept as content either `string`, `bytes` or instance inherent of `BaseIO`. 

### Generating a hash from file

Soon... The code already allow it, just need to complete this README.

### Saving file

Any change to file content can be saved with the code below. Changes in metadata of File are not applied to 
filesystem when saving.

```python
# Saving a new file
my_file.save()

# Saving a file previously loaded from file_system will throw a 
# exception `File.OperationNotAllowed` unless `allow_update` is set to `True` 
# or `create_backup` is set to `True`.
my_file.save(allow_update=True) # overwritten original file content
my_file.save(create_backup=True) # rename the old file as '<complete_filename>.bak' and create a new one
```

The following parameters are accepted in `save` method keyword arguments:

- `overwrite` (`bool`) - If file with same filename exists it will be overwritten.
- `save_hashes` (`bool`) - If hash generate for file should also be saved.
- `allow_search_hashes` (`bool`) - Allow hashes to be obtained from hash`s files already saved.
- `allow_update` (`bool`) - If file exists its content will be overwritten.
- `allow_rename` (`bool`) - If renaming a file and a file with the same name exists a new one will be created instead 
of overwriting it.
- `create_backup` (`bool`) - If file exists and its content is being updated the old content will be backup before saving.

### Customizing a pipeline

Soon... The code already allow it, just need to complete this README.

## Testing

Soon... I didn't create any automated test yet, but I intend to.

## Contributing

Contributions, issues and feature requests are welcome!

- Feel free to check [issues page](https://github.com/Gabriel-Fontenelle/Handler/issues). 

## Related Projects

Soon...

## Unsatisfying things that needs better code before version 1:

- The pipeline for hash generation with multiple hashes should not need to read the whole file for each hash algorithm. A solution is to have a distinct pipeline to work with hashes (probably the pipeline resource will be refactored the format of engine/adapter that can be extended).
- The Blake3 hasher should be added to the list of hashers.
- The option to generate an ecc for file recovery with customizable size and percent of recovery.
- Do the default thumbnail generator and thumbnail composer for multiple files inside a file packet (compressed container).
- When generating the thumbnail for a file inside a compressed file inside another compressed file the later compressed file will be load whole to memory and if its size is greater than the free memory the code will be killed. This need to be fixed with a warning that check the RAM available space (there is a class for that already) or a way to partial decompress a compressed block from the upper stream.
- Filename, path, save_to should be refactored to allow for both a absolute and relative name, thus allowing for compressing multiple files and for serializing without absolute paths.
- Code should be refactored to allow multi process execution for hashing, loading internal files and generating thumbnails.


## License

Copyright (C) 2021 Gabriel Fontenelle Senno Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
