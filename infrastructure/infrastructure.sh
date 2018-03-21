#!/usr/bin/env bash
set -e

ACTION=$1

shift 1

source venv/bin/activate && terraform "$ACTION" \
  -var "account_id=${ACCOUNT_ID}" \
  -var "cloudtrail_log_group_name=${CLOUDTRAIL_LOG_GROUP_NAME}" \
  -var "cloudtrail_name=${CLOUDTRAIL_NAME}" \
  -var "es_email_principals=${ES_AUTHORIZED_EMAILS}" \
  -var "cloudtrail_s3_bucket=${CLOUDTRAIL_S3_BUCKET}" \
  -var "es_domain_name=${ES_DOMAIN_NAME}" \
  -var "travis_user=${TRAVIS_USER}" \
  -var "aws_region=${AWS_REGION}" \
  -var "gcp_region=${GCP_REGION}" \
  -var "gcp_pubsub_authorized_service_accounts=${GCP_PUBSUB_AUTHORIZED_SERVICE_ACCOUNTS}" \
  $([[ "$ACTION" == "plan" ]] && echo -n "-detailed-exitcode" || echo -n "") \
  "$@"