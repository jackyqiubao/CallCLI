CREATE TABLE `3dartifacts` (
  `ArtifactID` CHAR(36) NOT NULL,
  `ProjectID` VARCHAR(64) NULL,
  `SiteID` VARCHAR(64) NULL,
  `LocationID` VARCHAR(64) NULL,
  `CoverageDate` VARCHAR(32) NULL,
  `InvestigationTypes` TEXT NULL,
  `MaterialTypes` TEXT NULL,
  `CulturalTerms` TEXT NULL,
  `Keywords` TEXT NULL,
  `CreatedTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `UploadedPics` BOOLEAN NULL,
  `3dModelCreatedStatus` VARCHAR(10) NULL,
  `3dModelFilePath` TEXT NULL,
  `LogFilePath` TEXT NULL,
  PRIMARY KEY (`ArtifactID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;