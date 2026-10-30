In order for `s31` to work, you will need to properly setup your AWS credentials. If this is running on your local machine, you will need to setup your [AWS security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html). Generally, this entails running installing the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and running `aws login`, which will automatically setup the proper credentials. Those credentials are unfortunately short-lived; you can setup longer-lived [access keys](https://docs.aws.amazon.com/sdkref/latest/guide/feature-static-credentials.html), though this is not recommended.

`s31`, however, is intended to run *on* an EC2 instance, in which case you should create an [IAM role](https://docs.aws.amazon.com/sdkref/latest/guide/access-assume-role.html) for the EC2 instance to assume and, in the `$HOME/.aws/config` (for computers running a linux/BSD variant) or `%userprofile%\.aws\config` (for Windows), add the following:

```
[profile]
role_arn = arn:aws:iam::123456789012:role/my-role-name
credential_source = Ec2InstanceMetadata
region = us-east-1
```

where, the value for `role_arn` is found on the "IAM > Roles > $IAMROLE" page in the "Summary" box under `ARN`.