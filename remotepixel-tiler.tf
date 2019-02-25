variable "stage_name" {
  description = "The stage name(production/staging/etc..)"
  default     = "production"
}

variable "project" {
  description = "The project name"
  default     = "remotepixel-tiler"
}

variable "token" {
  description = "Secret token"
}

module "landsat" {
  source = "git@github.com:developmentseed/tf-lambda-proxy-apigw.git?ref=v1"

  # General options
  project    = "${var.project}"
  stage_name = "${var.stage_name}"
  region     = "us-west-2"

  # Lambda options
  lambda_name    = "landsat"
  lambda_runtime = "python3.6"
  lambda_memory  = 512
  lambda_timeout = 5
  lambda_package = "package.zip"
  lambda_handler = "remotepixel_tiler.landsat.APP"

  lambda_env = {
    PYTHONWARNINGS                     = "ignore"
    GDAL_DATA                          = "/var/task/share/gdal"
    GDAL_CACHEMAX                      = "512"
    VSI_CACHE                          = "TRUE"
    VSI_CACHE_SIZE                     = "536870912"
    CPL_TMPDIR                         = "/tmp"
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES = "YES"
    GDAL_HTTP_MULTIPLEX                = "YES"
    GDAL_HTTP_VERSION                  = "2"
    GDAL_DISABLE_READDIR_ON_OPEN       = "FALSE"
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS   = ".TIF,.ovr"
    TOKEN                              = "${var.token}"
    MAX_THREADS                        = "20"
  }
}

resource "aws_iam_role_policy" "permissions" {
  name = "${module.landsat.lambda_role}-bucket-permission"
  role = "${module.landsat.lambda_role_id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::landsat-pds*"
    }
  ]
}
EOF
}

module "cbers" {
  source = "git@github.com:developmentseed/tf-lambda-proxy-apigw.git?ref=v1"

  # General options
  project    = "${var.project}"
  stage_name = "${var.stage_name}"
  region     = "us-east-1"

  # Lambda options
  lambda_name    = "cbers"
  lambda_runtime = "python3.6"
  lambda_memory  = 512
  lambda_timeout = 5
  lambda_package = "package.zip"
  lambda_handler = "remotepixel_tiler.cbers.APP"

  lambda_env = {
    PYTHONWARNINGS                     = "ignore"
    GDAL_DATA                          = "/var/task/share/gdal"
    GDAL_CACHEMAX                      = "512"
    VSI_CACHE                          = "TRUE"
    VSI_CACHE_SIZE                     = "536870912"
    CPL_TMPDIR                         = "/tmp"
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES = "YES"
    GDAL_HTTP_MULTIPLEX                = "YES"
    GDAL_HTTP_VERSION                  = "2"
    GDAL_DISABLE_READDIR_ON_OPEN       = "EMPTY_DIR"
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS   = ".TIF"
    AWS_REQUEST_PAYER                  = "requester"
    TOKEN                              = "${var.token}"
    MAX_THREADS                        = "20"
  }
}

resource "aws_iam_role_policy" "permissions" {
  name = "${module.cbers.lambda_role}-bucket-permission"
  role = "${module.cbers.lambda_role_id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::cbers-pds*",
        "arn:aws:s3:::cbers-meta-pds*"
      ]
    }
  ]
}
EOF
}

module "sentinel" {
  source = "git@github.com:developmentseed/tf-lambda-proxy-apigw.git?ref=v1"

  # General options
  project    = "${var.project}"
  stage_name = "${var.stage_name}"
  region     = "eu-central-1"

  # Lambda options
  lambda_name    = "sentinel"
  lambda_runtime = "python3.6"
  lambda_memory  = 512
  lambda_timeout = 5
  lambda_package = "package.zip"
  lambda_handler = "remotepixel_tiler.sentinel.APP"

  lambda_env = {
    PYTHONWARNINGS                     = "ignore"
    GDAL_DATA                          = "/var/task/share/gdal"
    GDAL_CACHEMAX                      = "512"
    VSI_CACHE                          = "TRUE"
    VSI_CACHE_SIZE                     = "536870912"
    CPL_TMPDIR                         = "/tmp"
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES = "YES"
    GDAL_HTTP_MULTIPLEX                = "YES"
    GDAL_HTTP_VERSION                  = "2"
    GDAL_DISABLE_READDIR_ON_OPEN       = "EMPTY_DIR"
    CPL_VSIL_CURL_CHUNK_SIZE           = "2000000"
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS   = ".jp2"
    AWS_REQUEST_PAYER                  = "requester"
    TOKEN                              = "${var.token}"
    MAX_THREADS                        = "20"
  }
}

resource "aws_iam_role_policy" "permissions" {
  name = "${module.sentinel.lambda_role}-bucket-permission"
  role = "${module.sentinel.lambda_role_id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::sentinel-s2*",
        "arn:aws:s3:::sentinel-s1*"
      ]
    }
  ]
}
EOF
}

module "cogeo" {
  source = "git@github.com:developmentseed/tf-lambda-proxy-apigw.git?ref=v1"

  # General options
  project    = "${var.project}"
  stage_name = "${var.stage_name}"
  region     = "us-east-1"

  # Lambda options
  lambda_name    = "cogeo"
  lambda_runtime = "python3.6"
  lambda_memory  = 512
  lambda_timeout = 5
  lambda_package = "package.zip"
  lambda_handler = "remotepixel_tiler.sentinel.APP"

  lambda_env = {
    PYTHONWARNINGS                     = "ignore"
    GDAL_DATA                          = "/var/task/share/gdal"
    GDAL_CACHEMAX                      = "512"
    VSI_CACHE                          = "TRUE"
    VSI_CACHE_SIZE                     = "536870912"
    CPL_TMPDIR                         = "/tmp"
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES = "YES"
    GDAL_HTTP_MULTIPLEX                = "YES"
    GDAL_HTTP_VERSION                  = "2"
    GDAL_DISABLE_READDIR_ON_OPEN       = "EMPTY_DIR"
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS   = ".TIF,.tif,.jp2,.vrt"
    TOKEN                              = "${var.token}"
    MAX_THREADS                        = "20"
  }
}

resource "aws_iam_role_policy" "permissions" {
  name = "${module.cogeo.lambda_role}-bucket-permission"
  role = "${module.cogeo.lambda_role_id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::remotepixel-pub*"
      ]
    }
  ]
}
EOF
}

# Outputs
output "landsat_endpoint" {
  description = "Landsat-8 dynamic tiler endpoint url"
  value       = "${module.landsat.api_url}"
}

output "cbers_endpoint" {
  description = "CBERS-4 dynamic tiler endpoint url"
  value       = "${module.cbers.api_url}"
}

output "sentinel_endpoint" {
  description = "Sentinel-2 dynamic tiler endpoint url"
  value       = "${module.sentinel.api_url}"
}

output "cogeo_endpoint" {
  description = "COGEO dynamic tiler endpoint url"
  value       = "${module.cogeo.api_url}"
}
