#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import lzma

from test.units import TestUnitBase
from test.units.compression import KADATH1, KADATH2


class TestMicrosoftCompressionFormat(TestUnitBase):

    def test_xpress_with_huffmann_01(self):
        compressed = bytes.fromhex(
            '0A51E5C0' '18008204' 'E7030000' '00000000' 'E7030000' '00000000' '16030000'
            '09000000000000000000000000000000040000000000880800000000009000009090000090009000000909000000000040664567559054459544546769090000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '09000000000000000000000000000000000000000000000099000000000000008709000000000000869000000000000076980009000000009507000000000000'
            '86880900000000009800080000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
            'C5F8814832E5F860200D5887B487C9550A423243278078004C908957A5193198E9931AD494BFF0AFC50C548305358EF11CB840C732CE06321979EDF6CD463ACD'
            'A7776519DA101CB50748E20427410FECAC660EC94E050FF91E94A89C3130EBFA7EE9D6BC13A306F578726286DD661B5B993ACE7D69280C4A103F0069E8150553'
            '3294CBBEE2D4A652DEC606BE405D3ED2BD240B785F7E5A82328E06A3AAABA6C92C2FAA41ABB738700C2ABE011576FED854718597B2A70A59A9C09D709CAD40A0'
            'A4CEDE4E780854C630C8CC277EAF72045CC4B883D32D0676C98CB33ECABB9605B9E02E91BA283803B6BDE0C23D72B9E7A9987A9BCDFF4D094546A250C72B893B'
            '3406B2AEE5C42E3CE475D24BFDA2A2EAFD7087ECA900CB0FFCA3580F57C4B20488F3EFE429BE398DE14628F968B3A618CA1D0FEC8673FE7B70083E2E8F638641'
            '0B49E4984EA3A4029D1C52AD095AAD8352A74BDC6CC63131EA684E19717731A878D2B7097B6067F4D0256D2386CD5CE4E124B8B55A9A79173EF9E172446E6AC1'
            '9371FC4953360BCBE2D7ACAF1AFDE8EC0C90851464E240DEF40562A947E3D00D22DE70E167168651D4C56A540F4EBC12CC96E1AA836A46A0ED53AA602A4B310D'
            'BED3B3D6A8543ADDCD09FA198DF8D12497FEE42B9FF39C3FA3AE4EBE07E3B6A8541ED0CBDB6D18B3917920F9BC50502E632A94FFDD65E26CD53F909860444003'
            'C91C64924803D2044765304BC754EC127DF500800000'
        )
        decompressed = str(compressed | self.load())
        self.assertEqual(KADATH1, decompressed)

    def test_xpress_with_uncompressed_tail(self):
        tail = bytes.fromhex(
            '55C4775EA9C86B823D0C9FE61190138A2554C76E7958BB920D9CEFF6E120639AF5E4177E49E80BA2'
            'DD2C3F06B1B0B3AAC574678E19785BB2ADBC8F16814003BA9504B79EE908ABC27D4CDF2651D053CA'
            '659407AEB998FBD24DDC2F362160A3DA352457BE89284BE21D6C7F46F1F0F3EA05B4A7CE59B89BF2'
            'EDFCCF56C18043FAD544F7DE2948EB02BD8C1F669110930AA5D447EEF9D83B128D1C6F7661A0E31A'
            '756497FEC9688B225DACBF863130332A45F4E70E99F8DB322D3C0F9601C0833A1584371E69882B42'
            'FDCC5FA6D150D34AE514872E39187B52CD5CAFB6A1E0235AB5A4D73E09A8CB629DECFFC67170736A'
            '8534274ED9381B726D7C4FD64100C37A55C4775EA9C86B823D0C9FE61190138A2554C76E7958BB92'
            '0D9CEFF6E120639AF5E4177E49E80BA2DD2C3F06B1B0B3AAC574678E19785BB2ADBC8F16814003BA'
        )
        head = bytes.fromhex(
            '0A51E5C018005C04400100040000000000000004000000000D010000000000000000000000000000'
            '00000000000000000000000000000000000000003033030000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000002000000'
            '00000000000000000000000000000000000000200000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '0000000074970000FF0000F9FFFF03000040010000'
        )
        self.assertEqual(next(head + tail | self.load()), 0x1000000 * B'ABCD' + tail)

    def test_xpress_with_compressed_tail(self):
        data = bytes.fromhex(
            '0A51E5C018000104001000040000000000000004000000000D010000000000000000000000000000000000000000000000000000000000000000000030330300'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000020000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000074970000FF0000F9FFFF0300000701000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000100000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000980000FFFC0F'
        )
        self.assertEqual(next(data | self.load()), 0x1000000 * B'ABCD' + 0x1000 * B'X')

    def test_xpress_even_chunks(self):
        data = lzma.decompress(bytes.fromhex(
            'FD377A585A000004E6D6B446020021011C00000010CF58CCE0056C00395D0005155B94D5C5CD79C6EFA959714B9F063045EB917F7D2D213E6E1747A2519D1671'
            '4AE8EF75380D68BFFCE1495F9AF6B6A79F7CE171E631EB00000000002CDDF5D04766A556000155ED0A00000093AEEF20B1C467FB020000000004595A'
        ))
        self.assertEqual(next(data | self.load()), 0x5000000 * B'ABCD')

    def test_xpress_01(self):
        compressed = bytes.fromhex(
            '0A51E5C0' '1800C903' 'E7030000' '00000000' 'E7030000' '00000000' '8B030000'
            '0000000054687265652074696D65732052616E646F6C70682043617274657220647265610D0000006D6564206F6620746865206D617276656C6C6F7573206369'
            '74792C207001C00072FE0108001008776173203801736E61746368B80161776179207768696C65207374696C6CE100706175200040507391026E920268696768'
            '205003726163652061626F76652069742E20415801676F6C646500000A526E1A036CB8006C79C80020626C617AE80169EB0173756E7365742C20776974682077'
            '616C6C06810021732C60026D706C654000636F6C6F6E6E61645900616E642061729A04627269646758079806760108001865696E6002B006626C652C2073696C'
            '7665722D626173B200666F756E7461696E7320500130000600707269736D6174696320737072A006000462726F61642073717561727002090370657266000160'
            '20756D880267617264656E1804A900776964652073747265657473110A6368696E6720626543000510747765F00664656C6963617465200101736A07626C6F73'
            '736F6D2D6CD8056E207572080439024082190069766F727920737461747578030004676CE80C5902726F77733B3C0B6F6E1001656570206E6F08852008727468'
            '77400420736C6F708801636C696D62E004746965729A06726000726F6F66AB036F6C6460848004207065616BF205626C8001686172626F757209036C69747420'
            '0E6C616EB80070086772617373803108047920636F6249012E2049742077D80F6120666576B8117C11676F64B804A000616E66617265208CC00080B000737570'
            '65726E616C207472756D70658808D20C20636C6173680001696D6DB805F8006379415000006D62616C732E204D797374657279206875A8096180047420697420'
            '6003636C6F7564D80500B802C892002103627588007320756E7669736974C10E6F0B0E3BB20A9001B41673746F6F6420627265617408040108686C6573FB0765'
            '7870656374616E7420100A7468617420F80375737472616450027061728000800061706574207468654006737765707420757020746F2068696DA90020706F69'
            '676E615A0010106E6379620373757370656E739A07616C6D6F73742D76616E697368B104651807E819745019705110636C61400EB8086C08013002696E67AC11'
            'E1006D616430129800206E65C10D6F20706C61391967A901776861590500000080780068616420616E20617765736F6D6520616E64206D6F6D656E746F757320'
            '706CFFFFFF076163652E00'
        )
        decompressed = str(compressed | self.load())
        self.assertIn(KADATH1, decompressed)

    def test_mszip_01(self):
        compressed = bytes.fromhex(
            '0A51E5C0' '18008A02' 'E7030000' '00000000' 'E7030000' '00000000' '30020000' '434B'
            '45534BB2D4300CE4283EC0BC770156142B166C282EA0249AD885FCC19213C2E96939F38A9D2DEBD3DD6AFF8C9D3958CAACE10795AD4A8BE12B75E31EB6CE9479'
            '0BF5192C72C8D40F16A943C39AEC7A04A4E3E17FFD491A90A7856C8DA8A393AE70C624885912F1C74643BD65992D63DA63C0A84E2B075AEAC121D97BF882DCBD'
            'CAC665CE10C4E5C24B5884FEA23ADDD53A8AB23DC2992C62B8883ED02C37611CD62AB514DAFCEC4DA84F4C4B4FDB0EACE074702A8880D622FC089AE4E0FEB690'
            'CEF0B38E6294CA4C6D3D69264B6BD0D6410A00965E690BFA7B50473B9FD0B83F87EBB55307F4D7DC336D4E1F2A99FAAC35A6B28785ED64D0DB58D24A06059170'
            'B759A4AAD6FC26E4FC472F77381DB55F684436900800BB603BDEABD7533FBF7486AE6ACC2D94DA2D9E0012546A43C52A292F006789FBE4D471E9B53EEFF6501B'
            '04E8D7840F3DB049E85247F70992CCD05CA8DCCAED9D542F48BC78E67BF86673F7149E0C093FFCB2D70DB810A4F284481ED601910A09E88EDC5C91B91A80238D'
            '4848390337DED72B2F2468FDFD021F108F0338E09061EE03723E756CFA0AF990654C6B8E72244DE68B7D6DF0F33D443F6CAD56AB1B81C922E0DF18F84FE3D5A8'
            'D86D4D82D74806F6862D4019EA04B84E0B44F4E46661B460150ECE936CAB692F54D66B76D3A10D0E989C4972557B3BA8247507660647FC9E5905789E83957B73'
            '68AD1FDFCAFFDB0607B8FE857D71353499FF64F7AAD331D6827B840F093FE564D8866779C6A198CB314BDE3FFD03'
        )
        decompressed = str(compressed | self.load())
        self.assertIn(KADATH1, decompressed)

    def test_xpress_02(self):
        compressed = bytes.fromhex(
            '0A51E5C0' '1800B003' '3E030000' '00000000' '3E030000' '00000000' 'FE020000'
            '000000004865206B6E6577207468617420666F722068696D20697473206D65616E696E6704000000206D757374206F6E63652068617665206265656E20737570'
            '72656D653BA8016F7508000201676820696E2077F9016379636C65202002696E6361726E6174696F6E2068C90164206B148280006E6F776E2069742CF9007768'
            '6574686572C101647265616D9B012077616B90032C9101636F00040000756C64206E6F742074656C6C2E2056616775656C7900022063616C6C65642075708810'
            '000020676C696D70736573206F662061206661722C1106676F74742005666972C805796F750400000274682C2077688800776F6E64657220616E6420706C6561'
            '73757265206C6198026E2084120410616C6C600665206D7973746572798102646179732C62016461C80561A8016475736B5001696B4400800065207374726F64'
            '65710374682070726F7068657469636B20746F3A026561674803736F9004006375A801E0046C757428051102736F6E673B20756E636C6F7369F00A6661710367'
            '61F900746F776100000403726420667572E208720175727072694A016D617276656C732E20427574206561636820C92A81006E69676874206173790973746F6F'
            '6420700B7468400E68C80020800162700C78067261F00D776948050881024074680C637572696F75732075726E73FA0663C9026E207261696C7A006C6F6F6B00'
            '0B6F666661088018206F7630069302757368A00073756E736574206369747921096265617548005105756E6561C00550C008006C7920696D6D616E656E63654A'
            '0E66656C200EB803626F6E64616765DA0A72A00F27732074310618047972616E6E6104676F64733B021460126E6F2077697365202310D0016C6561D8133A046C'
            '6F668003AC10641073706F4B126465736365200BC1067769880C6D61726D6FF0026C20666CF90873380075400B20016C650009442C7373F004644114380D7768'
            '65001074686F48037374726565744212656C2111776974636865727903000000206C6179206F757473707265616420616E64206265636B6F6E696E672E00'
        )
        decompressed = str(compressed | self.load())
        self.assertIn(KADATH2, decompressed)

    def _disabled_test_lzms_01(self):
        compressed = bytes.fromhex(
            '0A51E5C0' '1800C105' 'E7030000' '00000000' 'E7030000' '00000000' '16030000'
            '0C001FFF602BF3E01CBC93C73D7033E660EB7624CA103E92F4C2FC6B237F672A276733A7A851B78D6104346F5B520038B981D5C729A2EF658F1E371D18B203AB'
            '6BBFFA7E9D4DBB8C51BEF245000000C0057379299BCECD826BC3749659F22FB39263BDAC1ED1ACBBEBE030B4BB2BE619361836B80B59B2B232B76BE756EFC9B2'
            'E568F1B74E7E61B55C7F2D5AFA663159F2AC9FCB2E79D1E6D2AA3FBB966AE85B1B5B18F6B4D57BB8AAE61C96346FACD2E97696F6068721DD66F5F156D9C1D555'
            '737065777316C997CC96C2D566C5416605DD9A7B9DB56DB5856556D05571746365707865D9B796C66874616517F1DFDEE8E63649E6326077B4BE5F94AF14E7D2'
            'ECAA47CC8A3AB10B584D6F8EAC9ABB560EBB864F67B11B668D5B8766516DAD9CD76459AD34B1B6BC31EBD09AB8AD2DCD42449B0BB3F0C5AC7E351BAEADCE529A'
            '2DCCCDAA9BBBFC2C709B55322FBE9D39B2B7B36DFD96BFCBCC40C2B0DBD32581B85C916296C7F3E6E6C2E4CEB27A57906C16563ABACAE6D555AEEECD9AB65578'
            '6BD998C66B6117C76C6F99D60AEE4DCEA293C35E962B4BA3B3F0156B4B631BB35AC2BDB159FECA85DDA1D1C9BDB981C09595598A6E6FDAC877E6EEDEE4AEA356'
            'D6D9CE2E6EE7CAEAE8C22CA279726F7669999F9B5CDDB575185B4BDBDBDCDC1B9B5826F442AC12E9C2C6D2D8AA414BE7B2BBAA4E0CE4CC2DED0AB7AD72A4B3C2'
            '7D694D9676A74D6B595CE99D5DEBAE33932B83C3BACE95C985D5C5CD55616F726217B7796155D5389646573DCEA5C9C16192955C189D5BDD9B19E6371726D622'
            '57E5B1A5CD558C656C6297CC64656E696576D7CBD5DE19599A9C18F6AE5CD805F49A230B73737B637B1BB3E0CAD8E0DA2CA42C736C6C16B668D51D080B5DD99C'
            '5BDD5C9666E5D40B631303B102F3D8AC3F36ECAB5B1919DBDB99351904E242975665766F626115DD58989C652C08DA593588B95D4EE7EAC2E02E42B62AA3B3F6'
            'D8D2D02ABEBC0A2FCC9A89364617E636673D5657D89DB7930EC45209C2924797365645D6BDB1B195D9557D6D15235A8568F6064256FD85558264207265747261'
            '432068706C6F646E61522073656D6974206565726854'
        )
        decompressed = str(compressed | self.load())
        self.assertIn(KADATH1, decompressed)