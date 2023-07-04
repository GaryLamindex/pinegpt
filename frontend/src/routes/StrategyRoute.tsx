import OnePager from '../components/OnePager';

export function StrategyRoute() {
    // const location = useLocation();
    // const id = location.pathname.split('/')[2]; // split the pathname and take the second part after '/strategy/'
    // console.log('StrategyRoute is rendered with id', id);
    const hardcodedId = "0"; // example

    return <OnePager id={hardcodedId} />;
  
}
