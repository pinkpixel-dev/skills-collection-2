# Source notes

## Official source

- Title: *Synology File Station Official API*
- Publisher: Synology Inc.
- Guide release: 2023.03
- Downloaded: 2026-08-08
- URL: `https://global.synologydownload.com/download/Document/Software/DeveloperGuide/Package/FileStation/All/enu/Synology_File_Station_API_Guide.pdf`
- SHA-256: `f5dd1a120bcc1ed066d4d627cfc1130d8c872d7dedf609a44e777dd5d258c44c`
- Stored copy: `assets/Synology_File_Station_API_Guide.pdf`

## Extraction facts

The PDF container reports 5 physical pages, but `pdftotext -layout` yields 112 form-feed page breaks, 6,145 lines, and about 16,883 words. The document's printed pagination runs through page 111. Treat the stored PDF as complete despite the unusual PDF page metadata.

To inspect an exact section without loading the whole guide:

```sh
pdftotext -layout assets/Synology_File_Station_API_Guide.pdf /tmp/filestation-guide.txt
rg -n 'SYNO\.FileStation\.(Upload|Download)' /tmp/filestation-guide.txt
sed -n '3587,3897p' /tmp/filestation-guide.txt
```

Use temporary paths appropriate to the environment and remove generated text after inspection.

## Release history in the guide

- 2023.03: Minor fixes.
- 2021.03: DSM 7.0 API update and minor fixes.
- 2016.03: DSM 6.0 API update.
- 2013.08: Initial release.

## Scope limitations

The guide is the protocol reference provided by the user, but it is not proof of the exact APIs enabled on a specific NAS. DSM updates, installed package versions, account rights, and File Station configuration can change availability. Always run live `SYNO.API.Info` discovery.

The bundled Markdown is a task-oriented condensation and safety layer, not a verbatim reproduction. Consult the PDF for exact parameter availability tables and examples when version-specific precision matters.
