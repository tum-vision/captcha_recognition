<?php
set_time_limit(0);
/**
 * Script para la generación de CAPTCHAS
 *
 * @author  Jose Rodriguez <jose.rodriguez@exec.cl>
 * @license GPLv3
 * @link    http://code.google.com/p/cool-php-captcha
 * @package captcha
 * @version 0.3
 *
 */

$folder_name = $_GET['folder'];
$amount = (int) $_GET['amount'];

// The pictures will be saved to this folder
$folder = '../temp/' . $folder_name . '/';

$numberOfTrainImagesToGenerate = $amount;
$logAfterEveryNumberOfCaptchas = 1000;

$captcha = new SimpleCaptcha();
$captcha->folderTrain = $folder;
$captcha->minWordLength = 6;
$captcha->maxWordLength = 6;

//empty the folder first
echo("Deleting old files...\n");
flush();ob_flush();flush();
exec("rm -rf $folder");
exec("mkdir $folder");


for($j=0; $j<$numberOfTrainImagesToGenerate; $j++) {
  // Image generation
  $captcha->CreateTrainImage();
  if($j % $logAfterEveryNumberOfCaptchas == 0) {
    echo($j . " Training Samples have been created...(" . $captcha->skippedDuplicates . " skipped duplicates)\n");
    flush();ob_flush();flush();
    //ob_flush();flush();
    $captcha->skippedDuplicates = 0;
  }
}
echo($j . " Training Samples have been created...\n");
flush();ob_flush();flush();

/**
 * SimpleCaptcha class
 */
class SimpleCaptcha {
  
  public $vocalRule  = false;
  
  public $folderTrain  = '';
  public $folderTest  = '';

  /** Width of the image */
  public $width  = 180;

  /** Height of the image */
  public $height = 50;

  /** Dictionary word file (empty for random text) */
  public $wordsFile = '';

  /**
   * Path for resource files (fonts, words, etc.)
   *
   * "resources" by default. For security reasons, is better move this
   * directory to another location outise the web server
   *
   */
  public $resourcesPath = 'cool-captcha/resources/';

  /** Min word length (for non-dictionary random text generation) */
  public $minWordLength = 5;

  /**
   * Max word length (for non-dictionary random text generation)
   * 
   * Used for dictionary words indicating the word-length
   * for font-size modification purposes
   */
  public $maxWordLength = 9;

  /** Sessionname to store the original text */
  public $session_var = 'captcha';

  /** Background color in RGB-array */
  public $backgroundColor = array(255, 255, 255);

  /** Foreground colors in RGB-array */
  public $colors = array(
    array(0,0,0), // black
    //array(27,78,181), // blue
    //array(22,163,35), // green
    //array(214,36,7),  // red
  );

  /** Shadow color in RGB-array or null */
  public $shadowColor = null; //array(255, 0, 0);

  /** Horizontal line through the text */
  public $lineWidth = 0;

  /**
   * Font configuration
   *
   * - font: TTF file
   * - spacing: relative pixel space between character
   * - minSize: min font size
   * - maxSize: max font size
   */
  public $fonts = array(
      'Antykwa'  => array('spacing' => -3, 'minSize' => 23, 'maxSize' => 27, 'font' => 'AntykwaBold.ttf'),
//        'Candice'  => array('spacing' =>-1.5,'minSize' => 28, 'maxSize' => 31, 'font' => 'Candice.ttf'),
//        'DingDong' => array('spacing' => -2, 'minSize' => 24, 'maxSize' => 30, 'font' => 'Ding-DongDaddyO.ttf'),
//        'Duality'  => array('spacing' => -2, 'minSize' => 30, 'maxSize' => 38, 'font' => 'Duality.ttf'),
//        'Heineken' => array('spacing' => -2, 'minSize' => 24, 'maxSize' => 34, 'font' => 'Heineken.ttf'),
//        'Jura'     => array('spacing' => -2, 'minSize' => 28, 'maxSize' => 32, 'font' => 'Jura.ttf'),
//        'StayPuft' => array('spacing' =>-1.5,'minSize' => 28, 'maxSize' => 32, 'font' => 'StayPuft.ttf'),
//        'Times'    => array('spacing' => -2, 'minSize' => 28, 'maxSize' => 34, 'font' => 'TimesNewRomanBold.ttf'),
//        'VeraSans' => array('spacing' => -1, 'minSize' => 20, 'maxSize' => 28, 'font' => 'VeraSansBold.ttf'),
  );

  /** Wave configuracion in X and Y axes */
  public $Yperiod    = 12;
  public $Yamplitude = 14;
  public $Xperiod    = 11;
  public $Xamplitude = 5;

  /** letter rotation clockwise */
  public $maxRotation = 8;

  /**
   * Internal image size factor (for better image quality)
   * 1: low, 2: medium, 3: high
   */
  public $scale = 2;

  /** 
   * Blur effect for better image quality (but slower image processing).
   * Better image results with scale=3
   */
  public $blur = false;

  /** Debug? */
  public $debug = false;
  
  /** Image format: jpeg or png */
  public $imageFormat = 'png';

  /** GD image */
  public $im;
  
  public $skippedDuplicates = 0;


  public function __construct($config = array()) {
  }
  
  /**
  * This function generates a train image and double checks that this text sequence does not yet exist
  */
  public function CreateTrainImage() {
    /** Text creation */
    do {
      $text = $this->GetCaptchaText();
      if(file_exists($this->folderTrain . $text . '.png') ) {
        $this->skippedDuplicates++;
      }
    } 
    while (file_exists($this->folderTrain . $text . '.png') );
    
    /** Output */
    $this->CreateImage($text);
    $this->WriteImage($this->folderTrain . $text);
    $this->Cleanup();
  }
  
  /**
  * This function generates a train image and double checks that this text sequence does
  * neither exist in the train images set nor in the test images set
  */
  public function CreateTestImage() {
    /** Text creation */
    do {
      $text = $this->GetCaptchaText();
      if(file_exists($this->folderTrain . $text . '.png') || file_exists($this->folderTest . $text . '.png')) {
        $this->skippedDuplicates++;
      }
    }
    while (file_exists($this->folderTrain . $text . '.png') || file_exists($this->folderTest . $text . '.png'));
    
    /** Output */
    $this->CreateImage($text);
    $this->WriteImage($this->folderTrain . $text);
    $this->Cleanup();
  }

  public function CreateImage($text) {
    $ini = microtime(true);
  
    /** Initialization */
    $this->ImageAllocate();
  
    /** Text insertion */
    $fontcfg  = $this->fonts[array_rand($this->fonts)];
    $this->WriteText($text, $fontcfg);
  
    /** Save text for session cookie */
    $_SESSION[$this->session_var] = $text;
  
    /** Transformations */
    if (!empty($this->lineWidth)) {
      $this->WriteLine();
    }
    $this->WaveImage();
    if ($this->blur && function_exists('imagefilter')) {
      imagefilter($this->im, IMG_FILTER_GAUSSIAN_BLUR);
    }
    $this->ReduceImage();
  
  
    if ($this->debug) {
      imagestring($this->im, 1, 1, $this->height-8,
        "$text {$fontcfg['font']} ".round((microtime(true)-$ini)*1000)."ms",
        $this->GdFgColor
      );
    }
  }


  /**
   * Creates the image resources
   */
  protected function ImageAllocate() {
    // Cleanup
    /*if (!empty($this->im)) {
        imagedestroy($this->im);
    }*/
  
    $this->im = imagecreatetruecolor($this->width*$this->scale, $this->height*$this->scale);
    //$this->im = imagecreate($this->width*$this->scale, $this->height*$this->scale);
  
    // Background color
    $this->GdBgColor = imagecolorallocate($this->im,
      $this->backgroundColor[0],
      $this->backgroundColor[1],
      $this->backgroundColor[2]
    );
    imagefilledrectangle($this->im, 0, 0, $this->width*$this->scale, $this->height*$this->scale, $this->GdBgColor);
  
    // Foreground color
    $color           = $this->colors[mt_rand(0, sizeof($this->colors)-1)];
    $this->GdFgColor = imagecolorallocate($this->im, $color[0], $color[1], $color[2]);
  
    // Shadow color
    if (!empty($this->shadowColor) && is_array($this->shadowColor) && sizeof($this->shadowColor) >= 3) {
        $this->GdShadowColor = imagecolorallocate($this->im,
          $this->shadowColor[0],
          $this->shadowColor[1],
          $this->shadowColor[2]
        );
    }
  }
  
  
  /**
   * Text generation
   *
   * @return string Text
   */
  protected function GetCaptchaText() {
    $text = $this->GetDictionaryCaptchaText();
    if (!$text) {
        $text = $this->GetRandomCaptchaText();
    }
    return $text;
  }
  
  
  /**
   * Random text generation
   *
   * @return string Text
   */
  protected function GetRandomCaptchaText($length = null) {
    if (empty($length)) {
        $length = rand($this->minWordLength, $this->maxWordLength);
    }
  
    //$words  = "abcdefghijklmnopqrstvwyz23456789ABDEFGHLMNPRTY";
    $words  = "abcdefghijlmnopqrstvwyz";
    $vocals = "aeiou";
  
    $text  = "";
    $vocal = rand(0, 1);
    for ($i=0; $i<$length; $i++) {
      
      $text .= substr($words, mt_rand(0, strlen($words)-1), 1);
      
      /*if($this->vocalRule) {
        if ($vocal) {
          $text .= substr($vocals, mt_rand(0, strlen($vocals)-1), 1);
        } else {
          $text .= substr($words, mt_rand(0, strlen($words)-1), 1);
        }
        $vocal = !$vocal;
      }
      else {
        $text .= substr($words, mt_rand(0, strlen($words)-1), 1);
      }*/
    }
    return $text;
  }
  
  
  /**
   * Random dictionary word generation
   *
   * @param boolean $extended Add extended "fake" words
   * @return string Word
   */
  function GetDictionaryCaptchaText($extended = false) {
    if (empty($this->wordsFile)) {
      return false;
    }

    // Full path of words file
    if (substr($this->wordsFile, 0, 1) == '/') {
      $wordsfile = $this->wordsFile;
    } else {
      $wordsfile = $this->resourcesPath.'/'.$this->wordsFile;
    }

    if (!file_exists($wordsfile)) {
      return false;
    }

    $fp     = fopen($wordsfile, "r");
    $length = strlen(fgets($fp));
    if (!$length) {
      return false;
    }
    $line   = rand(1, (filesize($wordsfile)/$length)-2);
    if (fseek($fp, $length*$line) == -1) {
      return false;
    }
    $text = trim(fgets($fp));
    fclose($fp);


    /** Change ramdom volcals */
    if ($extended) {
      $text   = preg_split('//', $text, -1, PREG_SPLIT_NO_EMPTY);
      $vocals = array('a', 'e', 'i', 'o', 'u');
      foreach ($text as $i => $char) {
        if (mt_rand(0, 1) && in_array($char, $vocals)) {
          $text[$i] = $vocals[mt_rand(0, 4)];
        }
      }
      $text = implode('', $text);
    }

    return $text;
  }
  
  
  /**
   * Horizontal line insertion
   */
  protected function WriteLine() {
	
    $x1 = $this->width*$this->scale*.15;
    $x2 = $this->textFinalX;
    $y1 = rand($this->height*$this->scale*.40, $this->height*$this->scale*.65);
    $y2 = rand($this->height*$this->scale*.40, $this->height*$this->scale*.65);
    $width = $this->lineWidth/2*$this->scale;

    for ($i = $width*-1; $i <= $width; $i++) {
      imageline($this->im, $x1, $y1+$i, $x2, $y2+$i, $this->GdFgColor);
    }
  }
  
  
  /**
   * Text insertion
   */
  protected function WriteText($text, $fontcfg = array()) {
    if (empty($fontcfg)) {
      // Select the font configuration
      $fontcfg  = $this->fonts[array_rand($this->fonts)];
    }

    // Full path of font file
    $fontfile = $this->resourcesPath.'/fonts/'.$fontcfg['font'];


    /** Increase font-size for shortest words: 9% for each glyp missing */
    $lettersMissing = $this->maxWordLength-strlen($text);
    $fontSizefactor = 1+($lettersMissing*0.09);

    // Text generation (char by char)
    $x      = 20*$this->scale;
    $y      = round(($this->height*27/40)*$this->scale);
    $length = strlen($text);
    for ($i=0; $i<$length; $i++) {
      $degree   = rand($this->maxRotation*-1, $this->maxRotation);
      $fontsize = rand($fontcfg['minSize'], $fontcfg['maxSize'])*$this->scale*$fontSizefactor;
      $letter   = substr($text, $i, 1);

      if ($this->shadowColor) {
        $coords = imagettftext($this->im, $fontsize, $degree,
          $x+$this->scale, $y+$this->scale,
          $this->GdShadowColor, $fontfile, $letter);
      }
      $coords = imagettftext($this->im, $fontsize, $degree,
        $x, $y,
        $this->GdFgColor, $fontfile, $letter);
      $x += ($coords[2]-$x) + ($fontcfg['spacing']*$this->scale);
    }

    $this->textFinalX = $x;
  }
  
  
  /**
   * Wave filter
   */
  protected function WaveImage() {
    // X-axis wave generation
    $xp = $this->scale*$this->Xperiod*rand(1,3);
    $k = rand(0, 100);
    for ($i = 0; $i < ($this->width*$this->scale); $i++) {
      imagecopy($this->im, $this->im,
        $i-1, sin($k+$i/$xp) * ($this->scale*$this->Xamplitude),
        $i, 0, 1, $this->height*$this->scale);
    }

    // Y-axis wave generation
    $k = rand(0, 100);
    $yp = $this->scale*$this->Yperiod*rand(1,2);
    for ($i = 0; $i < ($this->height*$this->scale); $i++) {
      imagecopy($this->im, $this->im,
        sin($k+$i/$yp) * ($this->scale*$this->Yamplitude), $i-1,
        0, $i, $this->width*$this->scale, 1);
    }
  }
  
  
  /**
   * Reduce the image to the final size
   */
  protected function ReduceImage() {
    $imResampled = imagecreatetruecolor($this->width, $this->height);
    imagecopyresampled($imResampled, $this->im,
      0, 0, 0, 0,
      $this->width, $this->height,
      $this->width*$this->scale, $this->height*$this->scale
    );
    imagedestroy($this->im);
    $this->im = $imResampled;
  }
  
  
  /**
   * File generation
   */
  protected function WriteImage($filename) {
    if ($this->imageFormat == 'png' && function_exists('imagepng')) {
    //header("Content-type: image/png");
    imagetruecolortopalette($this->im, false, 255);
    //imagepng($this->im);
    imagepng($this->im, $filename . '.png', 0 ); 
    }
    else {
      header("Content-type: image/jpeg");
      imagejpeg($this->im, null, 80);
    }
  }
  
  
  /**
   * Cleanup
   */
  protected function Cleanup() {
    imagedestroy($this->im);
  }
}

?>
