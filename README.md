# flashImgGen
A tool to generate flash image for burning.
================================================
Useage:
-------
1. Modify start.bat, set python path.

2. Run start.bat.

3. Set output file, flash size.

4. In input files area, right-click mouse to add or delete input files.

5. Click buttons at bottom to generate image or save configuration.

Change History:
---------------

* 2020-01-14

	* Change method to get current dir.
	
	* Support add more files in one op.
		
	* Check file count and give warning.

* 2020-01-13

	* No need to enter file offset. Offset will map from file index, which is part of file name.
	
	* Check if file name contain index value when add file.
	
	* Check if file index is exist when add file.
	
* 2020-01-04
	
	* Update file ops to python 3.8
	
	* Seperate flash image module out of GUI

* 2020-01-03

	* Upgrade code to python 3.8

* 2019-12-17

	* Add progress bar.
	
	* Remove debug info.

* 2019-12-16

	* First usable version.
		