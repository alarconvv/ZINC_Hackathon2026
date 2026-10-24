import {Stack} from 'expo-router';
import {useFonts, Manrope_700Bold} from '@expo-google-fonts/manrope';
import {DMSans_400Regular,DMSans_600SemiBold} from '@expo-google-fonts/dm-sans';
import {PreferencesProvider} from '../theme';
import {Screen,Title} from '../components';
export default function RootLayout() {
 const [loaded,error]=useFonts({Manrope_700Bold,DMSans_400Regular,DMSans_600SemiBold});
 if(!loaded&&!error) return <PreferencesProvider><Screen><Title>Loading ZINC…</Title></Screen></PreferencesProvider>;
 return <PreferencesProvider><Stack screenOptions={{headerShown:false}}/></PreferencesProvider>;
}
