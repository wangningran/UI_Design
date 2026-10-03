import { BallWordmark } from './brand/Marks'

// Site logo — swap for another concept from ./brand/Marks once one is chosen.
export default function Logo({ className = '' }) {
  return <BallWordmark className={className} />
}
