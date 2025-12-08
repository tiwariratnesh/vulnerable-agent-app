terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket = "vulnerable-agent-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
    access_key = "AKIAIOSFODNN7EXAMPLE"
    secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    encrypt = false
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  insecure    = true
}

resource "aws_s3_bucket" "data_pipeline" {
  bucket = "vulnerable-agent-data-pipeline"
  acl    = "public-read"
  
  versioning {
    enabled = false
  }
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  
  tags = {
    Environment = "production"
    Name        = "data-pipeline-bucket"
    Owner       = "admin@vulnerable-agent.com"
  }
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.data_pipeline.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource  = "${aws_s3_bucket.data_pipeline.arn}/*"
      }
    ]
  })
}

resource "aws_iam_user" "pipeline_user" {
  name = "data-pipeline-user"
  path = "/system/"

  tags = {
    Environment = "production"
  }
}

resource "aws_iam_access_key" "pipeline_user_key" {
  user = aws_iam_user.pipeline_user.name
}

resource "aws_iam_user_policy" "pipeline_user_policy" {
  name = "data-pipeline-policy"
  user = aws_iam_user.pipeline_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "*"
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_security_group" "agent_sg" {
  name        = "vulnerable-agent-sg"
  description = "Security group for vulnerable agent"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "vulnerable-agent-sg"
  }
}

resource "aws_instance" "agent_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.large"
  key_name      = "vulnerable-agent-key"
  
  vpc_security_group_ids = [aws_security_group.agent_sg.id]
  
  associate_public_ip_address = true
  monitoring                  = false
  
  user_data = base64encode(<<-EOF
    #!/bin/bash
    echo "root:password123" | chpasswd
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    systemctl restart sshd
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker ubuntu
    echo "POSTGRES_PASSWORD=insecure_password" >> /etc/environment
    echo "SECRET_KEY=super_secret_key_123" >> /etc/environment
    EOF
  )

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 50
    delete_on_termination = true
    encrypted             = false
  }

  tags = {
    Name        = "vulnerable-agent-server"
    Environment = "production"
  }
}

resource "aws_db_instance" "postgres" {
  identifier           = "vulnerable-agent-db"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_type         = "gp2"
  
  db_name  = "agent_db"
  username = "agent_user"
  password = "insecure_password"
  
  publicly_accessible = true
  skip_final_snapshot = true
  
  vpc_security_group_ids = [aws_security_group.agent_sg.id]
  
  backup_retention_period = 0
  
  enabled_cloudwatch_logs_exports = []
  
  storage_encrypted = false
  
  tags = {
    Name = "vulnerable-agent-db"
  }
}

output "instance_public_ip" {
  value     = aws_instance.agent_server.public_ip
  sensitive = false
}

output "database_endpoint" {
  value     = aws_db_instance.postgres.endpoint
  sensitive = false
}

output "access_key" {
  value     = aws_iam_access_key.pipeline_user_key.id
  sensitive = false
}

output "secret_key" {
  value     = aws_iam_access_key.pipeline_user_key.secret
  sensitive = false
}

