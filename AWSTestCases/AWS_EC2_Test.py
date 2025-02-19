import boto3


class EC2Client:
    def __init__(self, AWS_REGION):
        self.AWS_REGION = AWS_REGION
        self.client = boto3.client('ec2', region_name=self.AWS_REGION)
        self.resource = boto3.resource('ec2', region_name=self.AWS_REGION)

    def describe_instance(self, instance_id):
        response = self.client.describe_instances(InstanceIds=[instance_id])
        responsexx = self.resource.Instance(instance_id)
        print(responsexx)
        '''securityG = response['Reservations'][0]['Instances'][0]["SecurityGroups"][0]["GroupId"]
        sgx = self.client.describe_security_groups()
        print(sgx['SecurityGroups'][0]['SecurityGroupArn'])'''
        return response, responsexx

    def ProcessDescribeInstances(self, Data):
        # Process Describe instance data from AWS. Defined couple of common tags, suit your needs
        global Host, Name, InstID, PubIP, Status, VPCId, InstanceType, ImageId
        for X in Data['Reservations']:
            for Y in X["Instances"]:
                PubIP = Y.get("PublicIpAddress", "NULL")
                VPCId = Y.get("VpcId", "NULL")
                InstID = Y.get("InstanceId", "NULL")
                InstanceType = Y.get("InstanceType", "NULL")
                ImageId = Y.get("ImageId", "NULL")
                Status = Y.get('State').get('Name')
                # Process Tags for some default values
                for Z in Y["Tags"]:
                    # Setting some default for Tad as unsure if it will exist
                    if Z["Key"] == 'CMDB_hostname':
                        Host = Z.get('Value', "NULL")

                    '''try:
                        Host
                    except:
                        Host = "Undefined"'''

                    if Z["Key"] == 'Name':
                        Name = Z.get('Value', "NULL")
                    '''try:
                        Name
                    except:
                        Name = "Undefined"'''

            try:
                print(InstID, Name, PubIP, Status, VPCId, InstanceType, ImageId)
            except Exception as e:
                print("Failed to get Instance information:" + str(e))

    def get_tag_value(self, instance, tag_key):
        return next((tag['Value'] for tag in instance['Tags'] if tag['Key'] == tag_key), '')

    def getStatus(self, instance_id):
        datax, datax1 = self.describe_instance(instance_id)
        print(datax['Reservations'][0]['Instances'][0]['ImageId'])
        print(datax1.block_device_mappings)
        # print(datax1.instance_id, datax1.network_interfaces_attribute)
        print(datax1.tags, datax1.image_id, datax1.instance_type, datax1.image)
        gettags = self.get_tag_value(datax['Reservations'][0]['Instances'][0], 'Name')
        print(gettags)
        #[0]>Instances>[0]>NetworkInterfaces>[0]>Groups>[0]>GroupId
        #self.ProcessDescribeInstances(Data=datax)


getec2 = EC2Client("us-east-1")
getec2.getStatus(instance_id='i-0dca07e7fd952ad31')
# print(xmt)
