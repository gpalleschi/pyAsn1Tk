<div style=”border: 1px solid #000″>
	<img src="icon/pyAsn1Tk.ico" alt="pyAsn1Tk"
		title="pyAsn1Tk" width="70" height="70" align="left"/>
	<h1 align="left">pyAsn1Tk</h1>	
</div>		

## Description

**A visual Asn1 BER reader written in Python using TKinter embedded package. This tool permits read and decode a binary file in ASN1 BER codification and saving visual result in a txt file.**

![image](https://drive.google.com/uc?export=view&id=1R08lLw_LtcVjt0q3bVw45XZQl_KL2HDo)  

You can use a convertion file *\{Se TAG312 and RAP15 CONV_FILE in project [ASN.1-Reader](https://github.com/gpalleschi/ASN.1-Reader)\}*.  

Conversion file is a text file and it has this format `<Tag Name>|<Conversion Type>|<Desc Tag>[|Regular Expression]`  

Field|Description
--------|----
`<Tag Name>`|Tag Name in format Id-Class or only Class (TAP Notation)
`<Conversion Type>`|Represent type of convertion to apply :<br>A for Hex to Ascii<br>B for Hex to Binary<br>N for Hex to Number
`<Desc Tag>`|Tag Description Name to show for tag
`[Regular Expression]`|Optional field to control value of a primitive Tag converted.<br>If expression is true will be showed CHECK OK in green after convertion<br>instead will be showed CHECK KO regexpr`<regularexpression>` in red

It's present a pyAsn1Tk.exe in /dist directory created for windows environment.  

## Prerequisites

`Python 3.x`  

## Built With

* [Visual Code Editor](https://code.visualstudio.com) 

## Authors

* **Giovanni Palleschi** - [gpalleschi](https://github.com/gpalleschi)

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE 3.0 License - see the [LICENSE](LICENSE) file for details
