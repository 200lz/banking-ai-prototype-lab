# Tokyo CDK bootstrap execution and cleanup

Recorded: 2026-09-09. Scope: the reviewed standard `CDKToolkit` bootstrap in
`ap-northeast-1`, qualifier `hnb659fds`, using the approved non-root Identity
Center profile `jdd-sandbox`. The user explicitly authorized this bootstrap,
including persistent `AdministratorAccess` on its CloudFormation execution role.
Same-account trust, no added external trust, and unchanged application runtime
IAM are part of that authorization. No further approval is needed for this exact
bootstrap scope.

**Bootstrap: PASS / PERFORMED.** The stack was created at 13:17:48 UTC, the CLI
completed with exit 0 at 13:18:44 UTC, and actual AWS verification completed at
13:21:27 UTC. All 25 recorded checks passed and all 11 reviewed resources reached
`CREATE_COMPLETE`. The deployed template matched the reviewed template. See the
[sanitized execution evidence](validation/cdk-bootstrap-2026-09-09.json).

**Current disposition (September 15): CLEANUP PASS.** The application was deployed,
passed nine infrastructure-only smoke checks and was removed. After dependency
review, both bootstrap asset versions and its image were removed, `CDKToolkit`
reached `DELETE_COMPLETE`, and its retained bucket, repository, five roles and
version parameter were verified absent. See [actual cleanup](final-validation-cleanup.md).
The original September 9 decision was to keep bootstrap for that deployment;
the remaining sections preserve its creation evidence and reusable procedure.
Live Bedrock remains **NOT TESTED / BLOCKED**, independently of infrastructure.

## Acceptance criteria

- Revalidate the approved account and non-root SSO actor privately, and explicitly
  target Tokyo. Record only identity-match booleans in public evidence.
- Use pinned CDK CLI `2.1140.0`, reviewed template version `32`, qualifier
  `hnb659fds`, public-access blocking, AWS-managed S3 encryption, no custom KMS
  key, and empty `TrustedAccounts` / `TrustedAccountsForLookup` parameters.
- Execute only the reviewed bootstrap. Do not deploy the application, remove its
  reservation of three, broaden runtime IAM, or introduce cross-account trust.
- Require a completed successful stack, then inspect its actual resources,
  outputs, version parameter, role policies/trust, bucket controls and ECR policy.
  Compare the observed inventory with the 11 expected resources below.
- Confirm no bootstrap-created workload API, Lambda function, database, model
  invocation or hosting site. Record an explicit keep/delete disposition.
- Preserve sanitized evidence with timestamps; omit account IDs, physical names
  containing account IDs, session ARNs, credentials and provider request IDs.

## Credential-free template verification

The reviewed local template is `.runtime/aws-review/bootstrap-template.yaml`.
Its captured byte SHA-256 is
`dc91dbee74bd71a259313d460f9cb4a64123d73e67d4bc7fad5d11a64f0ab9b6`.
The local CLI's `bootstrap --show-template` performs template inspection without
AWS calls. The template has 14 resource declarations, of which 11 are enabled
for the reviewed CLI configuration. A customer-managed KMS key, alias and example
permissions boundary are conditional and are not expected to be created.

```powershell
Get-FileHash -Algorithm SHA256 .runtime/aws-review/bootstrap-template.yaml
node infra/cdk/node_modules/aws-cdk/bin/cdk bootstrap --show-template
```

The raw template's empty KMS parameter differs from the CLI's effective new-stack
behavior. The approved command uses `--no-bootstrap-customer-key` explicitly;
do not deploy the raw YAML with unreviewed parameter defaults. The
[security review](aws-deployment-review.md) records the detailed policy assessment.

## Verified resource inventory

Actual resource reads confirmed the inventory below. Exact physical identifiers
are retained in the ignored operator inventory for cleanup; public evidence
redacts account-bearing names. The stack is `CREATE_COMPLETE`, its outputs are
present, and `/cdk-bootstrap/hnb659fds/version` contains `32`.

| Logical resource | Type | Expected behavior / deletion | Actual state |
| --- | --- | --- | --- |
| `StagingBucket` | S3 bucket | Private, versioned, SSE-KMS with AWS-managed S3 key; Retain | CREATE_COMPLETE |
| `StagingBucketPolicy` | S3 bucket policy | Deny non-TLS operations; deleted with stack | CREATE_COMPLETE |
| `ContainerAssetsRepository` | ECR repository | Private, immutable image tags; deletion requires empty repository | CREATE_COMPLETE |
| `FilePublishingRole` | IAM role | Same-account file-asset publishing; deleted with stack | CREATE_COMPLETE |
| `ImagePublishingRole` | IAM role | Same-account image-asset publishing; deleted with stack | CREATE_COMPLETE |
| `LookupRole` | IAM role | Same-account lookup; ReadOnlyAccess plus decrypt deny; deleted with stack | CREATE_COMPLETE |
| `FilePublishingRoleDefaultPolicy` | IAM inline policy resource | Scoped asset bucket/key access; deleted with stack | CREATE_COMPLETE |
| `ImagePublishingRoleDefaultPolicy` | IAM inline policy resource | Scoped repository access and wildcard ECR auth token; deleted with stack | CREATE_COMPLETE |
| `DeploymentActionRole` | IAM role | Same-account deployment and scoped execution-role passing; deleted with stack | CREATE_COMPLETE |
| `CloudFormationExecutionRole` | IAM role | CloudFormation service trust; AdministratorAccess; deleted with stack | CREATE_COMPLETE |
| `CdkBootstrapVersion` | SSM parameter | `/cdk-bootstrap/hnb659fds/version` = `32`; deleted with stack | CREATE_COMPLETE |

Actual IAM inspection confirmed all five role trust policies and the approved
`AdministratorAccess` attachment. Both external-trust parameters are empty.
S3 inspection confirmed all four public-access blocks, Tokyo location, versioning,
SSE-KMS and the TLS-deny bucket policy. ECR is in Tokyo, uses AES256 encryption
and immutable tags, and limits service image retrieval to this account/region.
The bootstrap created no customer-managed KMS key. Both the bucket and repository
were reported empty at verification.

Before any later cleanup, repeat complete object-version, delete-marker,
multipart-upload and image inventories. The published empty-at-verification
booleans are a point-in-time observation, not a guarantee about future assets.

The CloudFormation stack, S3 bucket, ECR repository and SSM parameter target
Tokyo. IAM roles and policies are account-global AWS resources by design, even
when their names contain the Tokyo region. This bootstrap creates no second
regional stack or external-account trust.

The four operator-facing roles use the same-account AWS account principal. IAM
may serialize this as a principal ending in `:root`; it delegates trust to that
account and does not identify the root user as the operator. Verify the actual
caller independently as the approved non-root SSO assumed role. The fifth role
trusts `cloudformation.amazonaws.com`. Empty external-trust parameters do not
narrow the standard deploy role's generic outbound permissions. [AWS account-principal semantics](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html)

## Historical September 9 retention decision and cleanup considerations

**September 9 disposition: KEEP FOR PLANNED SANDBOX DEPLOYMENT.** No cleanup had
been executed then; the observed bucket and repository were empty. The September
15 deployment and verified cleanup supersede that resource disposition.
Bootstrap resources contain no
application compute, but future S3 assets and
ECR images can incur storage charges. Current S3 versions have no automatic
expiry; noncurrent versions expire after 30 days and incomplete multipart uploads
after one day. ECR untagged images expire after 365 days; tagged images have no
expiry rule. No customer-managed KMS key was created. Do not infer a zero bill
from a successful bootstrap or an empty-resource assertion alone.

`StagingBucket` is retained, while `StagingBucketPolicy` has default Delete.
Deleting the stack therefore removes the TLS-deny policy from the retained
bucket. Public-access blocking, encryption and versioning remain bucket settings.
For an authorized complete teardown, delete the retained bucket immediately after
stack removal. If retaining the bucket deliberately, record its owner and
preserve equivalent TLS enforcement through a separately managed policy. A
nonempty ECR repository can fail CloudFormation deletion because the reviewed
template does not set `EmptyOnDelete`. [CloudFormation deletion behavior](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-deletionpolicy.html)

The retained administrative deployment role remains a privileged boundary while
the bootstrap is kept. Standard IAM roles/policies and the standard SSM version
parameter do not create running compute. This record does not measure an AWS
bill or assert that the account incurred no charges.

## Safe teardown procedure

This reusable procedure applies only
after cleanup has been authorized and every application using this regional
bootstrap has been removed or migrated. Bootstrap resources are shared by CDK
applications in the same account/region; checking only this portfolio stack is
insufficient. Preserve the actual inventory before deleting anything, stop asset
publishing during cleanup, and use the operator's approved SSO identity rather
than the bootstrap roles being deleted.

1. Revalidate the caller privately and set the intended account in
   `CDK_DEFAULT_ACCOUNT`. Obtain exact bucket/repository names from
   `list-stack-resources`, not a prefix search. Retain all five role names and
   the parameter name for post-deletion verification. Check stack termination
   protection; if enabled, stop until its removal is explicitly included in the
   teardown decision.
2. Enumerate all ECR images and all S3 object versions, delete markers and
   multipart uploads with complete pagination. If anything is present, use the
   reviewed-inventory procedure below. Do not use `aws s3 rm --recursive` as proof
   that a versioned bucket is empty.
3. After the repository and bucket are verified empty, delete `CDKToolkit` using
   CloudFormation and wait for `stack-delete-complete`. On `DELETE_FAILED`, inspect
   stack events and resolve the named resource; do not force-delete or silently
   retain failed resources.
4. Delete the retained empty S3 bucket with the verified expected account owner.
   Confirm the stack, ECR repository, five IAM roles, SSM version parameter and
   retained bucket are absent. Treat access-denied/timeouts as inconclusive,
   rather than interpreting every error as successful removal.
5. Record actual cleanup timestamps and remaining resources. Do not delete the
   AWS-managed S3 KMS key. Other application data, secrets and other regional
   bootstrap stacks remain outside this cleanup scope.

The following PowerShell commands illustrate the **empty-inventory path** and
fail before deletion if assets remain. Run from an authenticated operator shell
with AWS CLI on PATH. Physical identifiers are kept in memory and not printed.
Review the dependency check and cleanup authorization above before running it.

```powershell
$bootstrapFlags = @('--profile', 'jdd-sandbox', '--region', 'ap-northeast-1', '--no-cli-pager')
function Invoke-BootstrapAws {
    param([string[]]$Arguments)
    $result = & aws @bootstrapFlags @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'AWS operation failed; stop cleanup and inspect privately.' }
    if ($result) { ($result -join "`n") | ConvertFrom-Json }
}
$bootstrapExpectedAccount = $env:CDK_DEFAULT_ACCOUNT
if ($bootstrapExpectedAccount -notmatch '^\d{12}$') { throw 'Set the privately verified account.' }
$bootstrapIdentity = Invoke-BootstrapAws @('sts', 'get-caller-identity')
if ($bootstrapIdentity.Account -ne $bootstrapExpectedAccount -or
    $bootstrapIdentity.Arn -notmatch ':assumed-role/AWSReservedSSO_') {
    throw 'Expected approved account and non-root Identity Center session.'
}
$bootstrapStack = Invoke-BootstrapAws @('cloudformation', 'describe-stacks', '--stack-name', 'CDKToolkit')
if ($bootstrapStack.Stacks[0].EnableTerminationProtection) { throw 'Termination protection is enabled.' }
$bootstrapInventory = Invoke-BootstrapAws @('cloudformation', 'list-stack-resources', '--stack-name', 'CDKToolkit')
if (@($bootstrapInventory.StackResourceSummaries).Count -ne 11) { throw 'Unexpected resource count.' }
$bootstrapBucket = @($bootstrapInventory.StackResourceSummaries | Where-Object LogicalResourceId -eq 'StagingBucket').PhysicalResourceId
$bootstrapRepository = @($bootstrapInventory.StackResourceSummaries | Where-Object LogicalResourceId -eq 'ContainerAssetsRepository').PhysicalResourceId
if ($bootstrapBucket -ne "cdk-hnb659fds-assets-${bootstrapExpectedAccount}-ap-northeast-1" -or
    $bootstrapRepository -ne "cdk-hnb659fds-container-assets-${bootstrapExpectedAccount}-ap-northeast-1") {
    throw 'Unexpected physical resources; compare the actual inventory before continuing.'
}
$bootstrapVersions = Invoke-BootstrapAws @('s3api', 'list-object-versions', '--bucket', $bootstrapBucket, '--expected-bucket-owner', $bootstrapExpectedAccount)
$bootstrapUploads = Invoke-BootstrapAws @('s3api', 'list-multipart-uploads', '--bucket', $bootstrapBucket, '--expected-bucket-owner', $bootstrapExpectedAccount)
$bootstrapImages = Invoke-BootstrapAws @('ecr', 'list-images', '--repository-name', $bootstrapRepository, '--registry-id', $bootstrapExpectedAccount)
if ($bootstrapVersions.Versions -or $bootstrapVersions.DeleteMarkers -or
    $bootstrapUploads.Uploads -or $bootstrapImages.imageIds) {
    throw 'Nonempty assets: follow reviewed inventory cleanup, then rerun empty checks.'
}
Invoke-BootstrapAws @('cloudformation', 'delete-stack', '--stack-name', 'CDKToolkit')
Invoke-BootstrapAws @('cloudformation', 'wait', 'stack-delete-complete', '--stack-name', 'CDKToolkit')
Invoke-BootstrapAws @('s3api', 'delete-bucket', '--bucket', $bootstrapBucket, '--expected-bucket-owner', $bootstrapExpectedAccount)
```

For a **nonempty inventory**, preserve complete listings privately and review
specific assets for deletion before mutation. For ECR, submit at most 100 exact
image digests per `batch-delete-image` call; deleting a tag alone may leave the
underlying image. Inspect the returned `failures` collection. [ECR batch deletion](https://docs.aws.amazon.com/cli/latest/reference/ecr/batch-delete-image.html)
For S3, create a `delete-objects` request containing at most 1,000 exact
`{Key, VersionId}` pairs per batch, including delete-marker version IDs, and use
`--expected-bucket-owner`. Inspect returned `Errors` even when the CLI exits zero.
Abort each enumerated multipart upload using its exact key and upload ID. Repeat
complete read-only inventories until all four collections are empty, then follow
the stack/bucket deletion sequence above. Neither a delete marker nor deletion of
only the latest version removes all stored versions. [S3 version-aware batch deletion](https://docs.aws.amazon.com/cli/latest/reference/s3api/delete-objects.html)

## September 9 offline verification of this runbook

The reviewed template hash and conditional resource count were rechecked without
AWS access. Both PowerShell examples parsed successfully. The cleanup example
was executed only against an in-memory fake AWS command: an empty inventory
completed its expected sequence, while nonempty assets, an unexpected account
and enabled termination protection each stopped before a simulated deletion.
No real cleanup command was executed during these checks. Markdown parsing and
local evidence-link validation also passed.
