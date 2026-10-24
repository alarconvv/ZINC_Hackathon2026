import {router} from 'expo-router';
import {Screen,Title,Card,T,Button} from '../components';
import {useSession} from '../session';
export default function Stopped(){const {data}=useSession();return <Screen><Title>Session stopped</Title><Card><T accessibilityRole="alert">{data?.view?.stop_message||'Do not resume this session. Seek urgent medical help for severe or persistent symptoms.'}</T><Button title="Download or delete my data" variant="secondary" onPress={()=>router.push('/settings')}/></Card></Screen>;}
