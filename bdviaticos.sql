-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: sistema_viaticos
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ciudades`
--

DROP TABLE IF EXISTS `ciudades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ciudades` (
  `id_ciudad` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `provincia` varchar(100) DEFAULT NULL,
  `pais` varchar(50) DEFAULT 'Perú',
  `codigo_postal` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_ciudad`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ciudades`
--

LOCK TABLES `ciudades` WRITE;
/*!40000 ALTER TABLE `ciudades` DISABLE KEYS */;
INSERT INTO `ciudades` VALUES (1,'Lima','Lima','Perú',NULL),(2,'Arequipa','Arequipa','Perú',NULL),(3,'Trujillo','La Libertad','Perú',NULL);
/*!40000 ALTER TABLE `ciudades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturas`
--

DROP TABLE IF EXISTS `facturas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturas` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `ruc` varchar(11) NOT NULL,
  `serie` varchar(4) NOT NULL,
  `num_documento` varchar(20) NOT NULL,
  `modalidad` varchar(50) DEFAULT NULL,
  `fecha_emision` date NOT NULL,
  `tipo_comprobante` varchar(50) NOT NULL,
  `id_producto` int DEFAULT NULL,
  `id_proyecto` int DEFAULT NULL,
  `id_usuario` int NOT NULL,
  `id_ciudad` int DEFAULT NULL,
  `importe` decimal(10,2) NOT NULL,
  `incluye_igv` tinyint(1) DEFAULT '0',
  `urldoc` varchar(512) NOT NULL COMMENT 'URL del comprobante en la nube',
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_factura`),
  UNIQUE KEY `uk_factura_unica` (`ruc`,`serie`,`num_documento`),
  KEY `id_producto` (`id_producto`),
  KEY `id_ciudad` (`id_ciudad`),
  KEY `idx_factura_usuario` (`id_usuario`),
  KEY `idx_factura_proyecto` (`id_proyecto`),
  KEY `idx_factura_fechas` (`fecha_emision`,`fecha_registro`),
  CONSTRAINT `facturas_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE SET NULL,
  CONSTRAINT `facturas_ibfk_2` FOREIGN KEY (`id_proyecto`) REFERENCES `proyectos` (`id_proyecto`) ON DELETE SET NULL,
  CONSTRAINT `facturas_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `users` (`id_usuario`),
  CONSTRAINT `facturas_ibfk_4` FOREIGN KEY (`id_ciudad`) REFERENCES `ciudades` (`id_ciudad`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturas`
--

LOCK TABLES `facturas` WRITE;
/*!40000 ALTER TABLE `facturas` DISABLE KEYS */;
INSERT INTO `facturas` VALUES (1,'20123456789','F001','00012345','Electrónico','2023-11-01','Factura',1,1,3,1,850.00,1,'https://onedrive.com/facturas/f001-12345','2025-03-31 22:56:37'),(2,'20123456789','B001','00056789','Electrónico','2023-11-05','Boleta',3,1,3,2,120.50,0,'https://onedrive.com/facturas/b001-56789','2025-03-31 22:56:37'),(3,'20198765432','F001','00098765','Físico','2023-11-10','Factura',2,2,3,3,450.00,1,'https://onedrive.com/facturas/f001-98765','2025-03-31 22:56:37'),(4,'20123456789','F001','12345','','0000-00-00','',NULL,1,3,NULL,1500.50,0,'','2025-04-19 18:34:12'),(5,'27123456666','111','111','None','2025-04-24','Boleta',1,2,3,1,11.00,1,'20250419_181620_diagrama.png','2025-04-19 18:16:20'),(6,'27123456666','E005','00000','VIATICOS LIMA','2025-04-18','Boleta',2,1,3,2,30.00,0,'20250421_230557_impresora02.jpg','2025-04-19 18:35:35'),(8,'12345678910','F001','123456789','VIATICOS LIMA','2025-04-21','Factura',1,1,3,1,15.00,0,'20250421_233604_10476351109-R01-E001-71.pdf','2025-04-21 23:36:04');
/*!40000 ALTER TABLE `facturas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Hospedaje','Gastos de alojamiento en hoteles'),(2,'Transporte','Pasajes y movilidad local'),(3,'Alimentación','Gastos de comida durante viajes');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyectos`
--

DROP TABLE IF EXISTS `proyectos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyectos` (
  `id_proyecto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `presupuesto` decimal(10,2) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  PRIMARY KEY (`id_proyecto`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyectos`
--

LOCK TABLES `proyectos` WRITE;
/*!40000 ALTER TABLE `proyectos` DISABLE KEYS */;
INSERT INTO `proyectos` VALUES (1,'Proyecto Amazonas','Exploración en la selva',500000.00,'2023-01-15','2023-12-31'),(2,'Modernización Oficina','Actualización equipos',150000.00,'2023-03-01','2023-06-30'),(3,'Proyecto Alpha','Desarrollo web',10000.00,NULL,NULL);
/*!40000 ALTER TABLE `proyectos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `fullname` varchar(100) DEFAULT NULL,
  `rol` varchar(20) DEFAULT 'usuario',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`fullname`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Juan Pérez','hashed_password1','juan@empresa.com','admin'),(2,'María Gómez','hashed_password2','maria@empresa.com','usuario'),(3,'lapaza','$2b$12$o.vS18frq28YMHRabiz6ku4lZ2IUriwjSBwDtCUnxDPIQjY.yYYAa','Luis Apaza','usuario'),(4,'root','$2b$12$EeEL8.qSHOQC4sEhRpla0OR7.VCGbfbHzorHMHEAd62NNk/YMWJDK',NULL,'usuario');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-25 21:00:10
