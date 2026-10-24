import {router} from 'expo-router';
import {Screen,Title,Card,T,Button} from '../../components';
export default function Terms(){return <Screen><Title>Terms</Title><Card><T>Draft — pending legal review.</T><T>ZINC is a general wellness beta with content pending professional review. Follow clinician guidance and stop if you feel unwell. Public release terms are still being prepared.</T><Button title="Go back" variant="secondary" onPress={()=>router.back()}/></Card></Screen>;}
